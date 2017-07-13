from __future__ import absolute_import, division, print_function

from appr.formats.appr.kub import Kub


class Kpm(Kub):
    media_type = 'kpm'
    platform = "kubernetes"
    manifest_file = ['manifest.jsonnet', 'manifest.yaml', 'manifest.yml', 'kpm-manifest.jsonnet']

    @property
    def kubClass(self):
        return Kpm
