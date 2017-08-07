from __future__ import absolute_import, division, print_function
import hashlib
import json
import logging
import subprocess
import tempfile
import time

import requests
from requests.utils import urlparse

__all__ = ['Kubernetes', "get_endpoint"]

logger = logging.getLogger(__name__)

resource_endpoints = {
    "daemonsets":
        "apis/extensions/v1beta1/namespaces/{namespace}/daemonsets",
    "deployments":
        "apis/extensions/v1beta1/namespaces/{namespace}/deployments",
    "horizontalpodautoscalers":
        "apis/extensions/v1beta1/namespaces/{namespace}/horizontalpodautoscalers",
    "ingresses":
        "apis/extensions/v1beta1/namespaces/{namespace}/ingresses",
    "jobs":
        "apis/extensions/v1beta1/namespaces/{namespace}/jobs",
    "namespaces":
        "api/v1/namespaces",
    "replicasets":
        "apis/extensions/v1beta1/namespaces/{namespace}/replicasets",
    "persistentvolumes":
        "api/v1/namespaces/{namespace}/persistentvolumes",
    "persistentvolumeclaims":
        "api/v1/namespaces/{namespace}/persistentvolumeclaims",
    "services":
        "api/v1/namespaces/{namespace}/services",
    "serviceaccounts":
        "api/v1/namespaces/{namespace}/serviceaccounts",
    "secrets":
        "api/v1/namespaces/{namespace}/secrets",
    "configmaps":
        "api/v1/namespaces/{namespace}/configmaps",
    "replicationcontrollers":
        "api/v1/namespaces/{namespace}/replicationcontrollers",
    "pods":
        "api/v1/namespaces/{namespace}/pods",
    "statefulset":
        "apis/apps/v1beta1/namespaces/{namespace}/statefulsets",
    "storageclass":
        "apis/storage.k8s.io/v1beta1/statefulsets", }

resources_alias = {
    "ds": "daemonsets",
    "hpa": "horizontalpodautoscalers",
    "ing": "ingresses",
    "ingress": "ingresses",
    "ns": "namespaces",
    "sc": "storageclasses",
    "sfs": "statefulsets",
    "po": "pods",
    "pv": "persistentvolumes",
    "pvc": "persistentvolumeclaims",
    "rc": "replicationcontrollers",
    "svc": "services"}

ANNOTATIONS = {
    'protected': 'resource.appr/protected',
    'hash': 'resource.appr/hash',
    'version': 'package.appr/version',
    'parent': 'package.appr/parent',
    'rand': 'resource.appr/rand',
    'update-mode': 'resource.appr/update-mode',
    'package': 'package.appr/package'}


def get_endpoint(kind):
    name = None
    if kind in resource_endpoints:
        name = kind
    elif kind in resources_alias:
        name = resources_alias[kind]
    elif kind + "s" in resource_endpoints:
        name = kind + "s"
    else:
        return 'unknown'
    return resource_endpoints[name]


class Kubernetes(object):
    def __init__(self, namespace=None, endpoint=None, body=None, proxy=None):

        self.proxy = None
        if endpoint is not None and endpoint[0] == "/":
            endpoint = endpoint[1:-1]
        self.endpoint = endpoint
        self.body = body
        self.obj = None
        self.protected = False
        self._resource_load()
        self.kind = self.obj['kind'].lower()
        self.name = self.obj['metadata']['name']
        self.force_rotate = ANNOTATIONS['rand'] in self.obj['metadata'].get('annotations', {})
        self.namespace = self._namespace(namespace)
        self.result = None
        if proxy:
            self.proxy = urlparse(proxy)

    def _resource_load(self):
        self.obj = json.loads(self.body)
        if 'annotations' in self.obj['metadata']:
            if (ANNOTATIONS['protected'] in self.obj['metadata']['annotations'] and
                    self.obj['metadata']['annotations'][ANNOTATIONS['protected']] == 'true'):
                self.protected = True

    def _gethash(self, src):
        # Copy rand value
        if (src is not None and ANNOTATIONS['rand'] in src['metadata'].get('annotations', {}) and
                ANNOTATIONS['rand'] not in self.obj['metadata']['annotations']):
            self.obj['metadata']['annotations'][ANNOTATIONS['rand']] = src['metadata'][
                'annotations'][ANNOTATIONS['rand']]

        # TODO(ant31) it should hash before the custom annotations
        if ANNOTATIONS['hash'] in self.obj['metadata'].get('annotations', {}):
            if self.obj['metadata']['annotations'][ANNOTATIONS['hash']] is None:
                sha = hashlib.sha256(json.dumps(self.obj, sort_keys=True)).hexdigest()
                self.obj['metadata']['annotations'][ANNOTATIONS['hash']] = sha
            return self.obj['metadata']['annotations'][ANNOTATIONS['hash']]
        else:
            return None

    def _namespace(self, namespace=None):
        if namespace:
            return namespace
        elif 'namespace' in self.obj['metadata']:
            return self.obj['metadata']['namespace']
        else:
            return 'default'

    def create(self, force=False, dry=False, strategy='update'):
        """
          - Check if resource name exists
          - if it exists check if the apprhash is the same
          - if not the same delete the resource and recreate it
          - if force == true, delete the resource and recreate it
          - if doesnt exists create it
        """
        force = force or self.force_rotate
        r = self.get()
        if r is not None:
            rhash = r['metadata'].get('annotations', {}).get(ANNOTATIONS['hash'], None)
        objhash = self._gethash(r)
        f = tempfile.NamedTemporaryFile()
        method = "apply"
        if self.proxy:
            method = "create"
            strategy = "replace"

        cmd = [method, '-f', f.name]

        f.write(json.dumps(self.obj))
        f.flush()
        if r is None:
            self._call(cmd, dry=dry)
            return 'created'
        elif (objhash is None or rhash == objhash) and force is False:
            return 'ok'
        elif rhash != objhash or force is True:
            if self.protected:
                return 'protected'
            if strategy == 'replace':
                self.delete(dry=dry)
                action = "replaced"
            elif strategy == "update":
                action = "updated"
            else:
                raise ValueError("Unknown action %s" % action)
            self._call(cmd, dry=dry)
            return action

    def get(self):
        cmd = ['get', self.kind, self.name, '-o', 'json']
        try:
            self.result = json.loads(self._call(cmd))
            return self.result
        except RuntimeError:
            return None
        except (requests.exceptions.HTTPError) as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

    def delete(self, dry=False, **kwargs):
        cmd = ['delete', self.kind, self.name]
        if self.protected:
            return 'protected'
        r = self.get()
        if r is not None:
            self._call(cmd, dry=dry)
            return 'deleted'
        else:
            return 'absent'

    def wait(self, retries=3, seconds=1):
        r = 1
        time.sleep(seconds)
        obj = self.get()
        while (r < retries and obj is None):
            r += 1
            time.sleep(seconds)
            obj = self.get()
        return obj

    def exists(self):
        r = self.get()
        if r is None:
            return False
        else:
            return True

    def _call(self, cmd, dry=False):
        command = ['kubectl'] + cmd + ["--namespace", self.namespace]
        if not dry:
            if self.proxy is not None:
                return self._request(cmd[0])
            else:
                try:
                    return subprocess.check_output(command, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError("Kubernetes failed to create %s (%s): "
                                       "%s" % (self.name, self.kind, e.output))
        else:
            return True

    def _request(self, method):
        if method == 'create':
            headers = {'Content-Type': 'application/json'}
            method = 'post'
            url = "%s/%s" % (self.proxy.geturl(), self.endpoint)
            return requests.post(url, data=self.body, headers=headers)
        else:
            url = "%s/%s/%s" % (self.proxy.geturl(), self.endpoint, self.name)
            query = getattr(requests, method)
            r = query(url)
            r.raise_for_status()
            return r.content
