from cnr.models.kv.package_kv_base import PackageKvBase
from cnr.models.kv.etcd.models_index import ModelsIndexEtcd


class Package(PackageKvBase):
    index_class = ModelsIndexEtcd
