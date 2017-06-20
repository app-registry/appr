from appr.models.kv.package_kv_base import PackageKvBase
from appr.models.kv.etcd.models_index import ModelsIndexEtcd


class Package(PackageKvBase):
    index_class = ModelsIndexEtcd
