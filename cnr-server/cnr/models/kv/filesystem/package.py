from cnr.models.kv.package_kv_base import PackageKvBase
from cnr.models.kv.filesystem.models_index import ModelsIndexFilesystem


class Package(PackageKvBase):
    index_class = ModelsIndexFilesystem
