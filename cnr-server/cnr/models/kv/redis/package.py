from cnr.models.kv.package_kv_base import PackageKvBase
from cnr.models.kv.redis.models_index import ModelsIndexRedis


class Package(PackageKvBase):
    index_class = ModelsIndexRedis
