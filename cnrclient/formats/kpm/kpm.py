from cnrclient.formats.kub_base import KubBase


class Kpm(KubBase):
    media_type = 'kpm'
    platform = "kubernetes"
    manifest_file = ['manifest.jsonnet', 'manifest.yaml']
