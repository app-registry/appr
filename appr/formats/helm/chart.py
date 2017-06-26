from appr.formats.helm.manifest_chart import ManifestChart
from appr.formats.kub_base import KubBase


class Chart(KubBase):
    media_type = "helm"
    platform = "helm"
    manifest_file = ['Chart.yml', 'Chart.yaml']

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
