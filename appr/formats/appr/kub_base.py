from __future__ import absolute_import, division, print_function

import copy
import json
import os.path
import shutil
import tempfile

import yaml

from appr.discovery import ishosted, split_package_name
from appr.formats.appr.manifest_jsonnet import ManifestJsonnet
from appr.formats.base import FormatBase
from appr.utils import convert_utf8, mkdir_p, parse_version_req
from appr.platforms.kubernetes import ANNOTATIONS


class KubBase(FormatBase):
    media_type = "kpm"
    target = "kubernetes"

    def __init__(self, name, version=None, variables=None, shards=None, namespace=None,
                 endpoint=None, resources=None, ssl_verify=True, **kwargs):
        super(KubBase, self).__init__(name, version=version, endpoint=endpoint,
                                      ssl_verify=ssl_verify, **kwargs)

        if shards.__class__ in [str, unicode]:
            shards = json.loads(shards)

        if variables is None:
            variables = {}

        self.endpoint = endpoint

        self._dependencies = None
        self._resources = None
        self._deploy_name = name
        self._deploy_shards = shards
        self._deploy_resources = resources
        self._package = None
        self._manifest = None
        self.namespace = namespace
        if self.namespace:
            variables["namespace"] = self.namespace

        self._deploy_vars = variables
        self._variables = None

        self.tla_codes = {"variables": self._deploy_vars}
        if shards is not None:
            self.tla_codes["shards"] = shards

    def create_kub_resources(self, resources):
        r = []
        for resource in resources:
            name = resource['metadata']['name']
            kind = resource['kind'].lower()
            protected = resource.get('annotations', {}).get(ANNOTATIONS['protected'], False)
            r.append({
                "file": "%s-%s.yaml" % (name, kind),
                "name": name,
                "generated": True,
                "order": -1,
                "protected": protected,
                "value": resource,
                "patch": [],
                "variables": {},
                "type": kind})
        return r

    def _create_manifest(self):
        return ManifestJsonnet(self.package, {"params": json.dumps(self.tla_codes)})

    @property
    def author(self):
        return self.manifest.package['author']

    @property
    def version(self):
        return self.manifest.package['version']

    @property
    def description(self):
        return self.manifest.package['description']

    @property
    def name(self):
        return self.manifest.package['name']

    @property
    def variables(self):
        if self._variables is None:
            self._variables = copy.deepcopy(self.manifest.variables)
            self._variables.update(self._deploy_vars)
        return self._variables

    @property
    def kubClass(self):
        raise NotImplementedError

    def _fetch_deps(self):
        self._dependencies = []
        for dep in self.manifest.deploy:
            if dep['name'] != '$self':
                # if the parent app has discovery but not child,
                # use the same domain to the child
                if ishosted(self._deploy_name) and not ishosted(dep['name']):
                    dep['name'] = "%s/%s" % (split_package_name(self._deploy_name)[0], dep['name'])
                variables = dep.get('variables', {})
                variables['kpmparent'] = {
                    'name': self.name,
                    'shards': self.shards,
                    'variables': self.variables}
                kub = self.kubClass(dep['name'], endpoint=self.endpoint,
                                    version=parse_version_req(dep.get('version', None)),
                                    variables=variables,
                                    resources=dep.get('resources', None), shards=dep.get(
                                        'shards', None), namespace=self.namespace)
                self._dependencies.append(kub)
            else:
                self._dependencies.append(self)
        if not self._dependencies:
            self._dependencies.append(self)

    @property
    def dependencies(self):
        if self._dependencies is None:
            self._fetch_deps()
        return self._dependencies

    def resources(self):
        if self._resources is None:
            self._resources = self.manifest.resources
        return self._resources

    @property
    def shards(self):
        shards = self.manifest.shards
        if self._deploy_shards is not None and len(self._deploy_shards):
            shards = self._deploy_shards
        return shards

    def build_tar(self, dest="/tmp"):
        package_json = self.build()

        tempdir = tempfile.mkdtemp()
        dest = os.path.join(tempdir, self.manifest.package_name())
        mkdir_p(dest)
        index = 0
        for kub in self.dependencies:
            index = kub.prepare_resources(dest, index)

        with open(os.path.join(dest, ".package.json"), mode="w") as f:
            f.write(json.dumps(package_json))

        tar = self.make_tarfile(dest)
        tar.flush()
        tar.seek(0)
        shutil.rmtree(tempdir)
        return tar.read()

    def prepare_resources(self, dest="/tmp", index=0):
        for resource in self.resources():
            index += 1
            path = os.path.join(dest, "%02d_%s_%s" % (index, self.version, resource['file']))
            f = open(path, 'w')
            f.write(yaml.safe_dump(convert_utf8(resource['value'])))
            resource['filepath'] = f.name
            f.close()
        return index

    def build(self):
        raise NotImplementedError

    def convert_to(self):
        raise NotImplementedError

    def deploy(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError
