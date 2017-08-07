from __future__ import absolute_import, division, print_function

from appr.formats.base import FormatBase
from appr.formats.helm.manifest_chart import MANIFEST_FILES, ManifestChart


class Chart(FormatBase):
    media_type = "helm"
    platform = "helm"
    manifest_file = MANIFEST_FILES

    def _create_manifest(self):
        return ManifestChart(self.package)

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
    def resources(self):
        return self.package.files
