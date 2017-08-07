from __future__ import absolute_import, division, print_function

import os.path

import yaml

from appr.formats.appr.manifest import ManifestBase
from appr.pack import all_files
from appr.render_jsonnet import RenderJsonnet, yaml_to_jsonnet

__all__ = ['ManifestJsonnet']

MANIFEST_FILES = ['manifest.jsonnet', 'manifest.yaml', 'manifest.yml', 'kpm-manifest.jsonnet']


class ManifestJsonnet(ManifestBase):
    def __init__(self, package=None, tla_codes=None):
        self.tla_codes = tla_codes
        if package is not None:
            self._load_from_package(package)
        else:
            self._load_from_path()

        super(ManifestJsonnet, self).__init__()

    def _isjsonnet(self, package):
        if "manifest.yaml" in package.files:
            return False
        elif "manifest.jsonnet" in package.files or "appr.jsonnet":
            return True
        else:
            raise RuntimeError("Unknown manifest format")

    def _load_from_package(self, package):
        if self._isjsonnet(package):
            self._load_jsonnet(package.manifest, package.files)
        else:
            self._load_yaml(package.manifest, package.files)

    def _load_from_path(self):
        for filepath in MANIFEST_FILES:
            if os.path.exists(filepath):
                mfile = filepath
                break
        _, ext = os.path.splitext(mfile)
        with open(mfile) as f:
            auth_files = all_files()
            files = dict(zip(auth_files, [None] * len(auth_files)))
            if ext == '.jsonnet':
                self._load_jsonnet(f.read(), files)
            else:
                self._load_yaml(f.read(), files)

    def _load_jsonnet(self, jsonnetstr, files):
        k = RenderJsonnet(files)
        r = k.render_jsonnet(jsonnetstr, self.tla_codes)
        self.update(r)

    def _load_yaml(self, yamlstr, files):
        try:
            jsonnetstr = yaml_to_jsonnet(yamlstr, self.tla_codes)
            files['manifest.jsonnet'] = jsonnetstr
            self._load_jsonnet(jsonnetstr, files)
        except yaml.YAMLError as exc:
            print('Error in configuration file:')
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark  # pylint: disable=E1101
                print('Error position: (%s:%s)' % (mark.line + 1, mark.column + 1))
            raise exc
