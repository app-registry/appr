from __future__ import absolute_import, division, print_function

from appr.formats.appr.kub import Kub
from appr.formats.appr.manifest import Manifest


class KubPlain(Kub):
    media_type = 'kubernetes'
    platform = "kubernetes"

    @property
    def _create_manifest(self):
        return Manifest(self._deploy_name, self._deploy_version)

    def add_resources(self, k8s_resources):
        self.manifest[
            'resources'] = self.manifest.resources + self.create_kub_resources(k8s_resources)
