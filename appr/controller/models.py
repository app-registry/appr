import os

import tempfile
import yaml
from appr.utils import get_media_type, content_media_type, manifest_media_type
from copy import deepcopy
import logging
import requests
from kubernetes import client as k8s_client, config, watch
from appr.pack import pack_kub, ApprPackage
from appr.utils import package_filename, mkdir_p
from appr.exception import PackageAlreadyExists

CRD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crd")

logger = logging.getLogger('k8s_events')

logger.setLevel(logging.DEBUG)

config.load_kube_config()
v1 = k8s_client.CoreV1Api()
v1ext = k8s_client.ExtensionsV1beta1Api()
custom_api = k8s_client.CustomObjectsApi()


class CrdModel(object):
    kind = None

    def __init__(self, name):
        self.cr_instance = self.generate_cr(self.kind, name)
        self.status = ''

    def _filename(self):
        raise NotImplementedError

    @property
    def name(self):
        return self.cr_instance['metadata']['name']

    @name.setter
    def name(self, value):
        self.cr_instance['metadata']['name'] = value

    @property
    def spec(self):
        return self.cr_instance['spec']

    @spec.setter
    def spec(self, value):
        self.cr_instance['spec'] = value

    def add_label(self, key, value):
        self.cr_instance['metadata'][key] = value

    def add_field(self, key, value):
        self.cr_instance['spec'][key] = value

    def transform(self):
        pass

    def render(self):
        self.transform()
        self.validate()
        return self.cr_instance

    def write_to_file(self, dest=".", force=True):
        filepath = os.path.join(dest, self._filename() + ".yaml")
        if not force and os.path.isfile(filepath):
            raise PackageAlreadyExists("release-file already exists")
        with open(filepath, "w") as output:
            output.write(yaml.safe_dump(self.render()))
        return filepath

    def generate_cr(self, kind, name, spec=None, labels=None, annotations=None):
        cr_instance = {
            "apiVersion": "manifest.k8s.io/v1alpha1",
            "kind": kind,
            "metadata": {
                "name": name,
                "annotations": {},
                "labels": {}
            },
            "spec": {}
        }

        if spec:
            cr_instance['spec'] = spec
        if labels:
            cr_instance['metadata']['labels'] = labels
        if annotations:
            cr_instance['metadata']['annotations'] = annotations
        return cr_instance

    def validate(self):
        return True


class DescriptorCr(CrdModel):
    kind = "Descriptor"

    def __init__(self, name, media_type=None):
        super(DescriptorCr, self).__init__(name)
        self.media_type = media_type

    @property
    def media_type(self):
        return self.spec['mediaType']

    @media_type.setter
    def media_type(self, value):
        self.add_field('mediaType', value)

    def _filename(self):
        return "descriptor.yaml"

    def validate(self):
        if not self.spec.get('mediaType', None):
            raise ValueError('Missing spec.mediaType')
        return True

    def transform(self):
        self.cr_instance['metadata']['labels']['mediaType'] = self.media_type


class PackageCr(DescriptorCr):
    kind = "Package"
    crd_plural = 'packages'
    crd_group = 'manifest.k8s.io'
    crd_version = 'v1alpha'

    def __init__(self, name, version, media_type=None, descriptor=None):
        super(PackageCr, self).__init__(name, media_type)
        if descriptor:
            self.descriptor = deepcopy(descriptor)
            self.spec.update(self.descriptor['spec'])
            self.cr_instance['metadata']['labels'].update(self.descriptor['metadata']['labels'])
            self.cr_instance['metadata']['annotations'].update(
                self.descriptor['metadata']['annotations'])
        self.add_field('packageName', name)
        self.add_field('packageVersion', version)
        self._appr_package = None

    @classmethod
    def load(cls, resource):
        return cls(resource['spec']['packageName'], resource['spec']['packageVersion'],
                   descriptor=resource)

    def transform(self):
        self.name = "%s.%s" % (self.spec['packageName'], self.version)
        self.cr_instance['metadata']['labels']['digest'] = self.cr_instance['spec']['content'][
            'digest'][0:10]
        self.cr_instance['metadata']['labels']['packageName'] = self.package_name
        self.cr_instance['metadata']['labels']['mediaType'] = self.media_type

    @property
    def version(self):
        return self.spec['packageVersion']

    @version.setter
    def version(self, value):
        self.add_field('packageVersion', value)

    @property
    def package_name(self):
        return self.spec['packageName']

    def validate(self):
        if self.name != "%s.%s" % (self.package_name, self.version):
            raise ValueError("name must be packageName.packageVersion")
        if not self.version:
            raise ValueError("Missing spec.packageVersion")
        if not self.spec.get('mediaType', None):
            raise ValueError('Missing spec.mediaType')
        if not self.spec.get('content', None):
            raise ValueError('Missing spec.content')
        if not self.spec['content'].get('size', None):
            raise ValueError('Missing spec.content.size')
        if not self.spec['content'].get('digest', None):
            raise ValueError('Missing spec.content.digest')
        if not self.spec['content'].get('source', None):
            raise ValueError('Missing spec.content.source')

        return True

    def _filename(self):
        return package_filename(self.package_name, self.version, self.media_type)

    def prepare_content(self, path=".", prefix=None):
        filename = self._filename()
        kubepath = os.path.join(tempfile.gettempdir(), filename + ".tar.gz")
        pack_kub(kubepath, srcpath=path, prefix=prefix)
        with open(kubepath, 'rb') as kubefile:
            appr_package = ApprPackage(kubefile.read(), b64_encoded=False)
        os.remove(kubepath)
        return appr_package

    def add_blob(self, srcpath=".", prefix=None):
        appr_package = self.prepare_content(srcpath, prefix)
        self._add_source(appr_package, {'blob': appr_package.b64blob})

    def _add_source(self, appr_package, source):
        self.add_field('content', {
            'source': source,
            'size': appr_package.size,
            'digest': appr_package.digest
        })

    def add_url(self, url):
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        appr_package = ApprPackage(resp.content, b64_encoded=False)
        self._add_source(appr_package, {'urls': [url]})

    @property
    def content(self):
        return self.spec.get('content', None)

    @property
    def content_source(self):
        return self.spec.get('content', {}).get('source', {})

    @property
    def appr_package(self):
        if self._appr_package is None:
            if 'blob' in self.content_source:
                self._appr_package = ApprPackage(self.content_source['blob'], b64_encoded=True)
            elif 'urls' in self.content_source:
                resp = requests.get(self.content_source['urls'][0], stream=True)
                resp.raise_for_status()
                self._appr_package = ApprPackage(resp.content, b64_encoded=False)
            else:
                raise ValueError("missing content")
        return self._appr_package

    def extract(self, dest=".", tarball=True):
        appr_package = self.appr_package
        if not tarball:
            appr_package.extract(dest)
        else:
            mkdir_p(dest)
            dest = os.path.join(dest, self._filename() + ".tar.gz")
            appr_package.pack(dest)
        return dest

    @classmethod
    def get(cls, name, namespace='default'):
        cls.load(
            custom_api.get_namespaced_custom_object(group=cls.crd_group, version=cls.crd_version,
                                                    plural=cls.crd_plural, name=name,
                                                    namespace=namespace))
