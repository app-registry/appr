from appr.models.kv.package_kv_base import PackageKvBase
from appr.models.kv.filesystem.models_index import ModelsIndexFilesystem


class Package(PackageKvBase):
    index_class = ModelsIndexFilesystem
