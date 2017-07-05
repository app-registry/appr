from __future__ import absolute_import, division, print_function

from appr.models.kv.package_kv_base import PackageKvBase
from appr.models.kv.redis.models_index import ModelsIndexRedis


class Package(PackageKvBase):
    index_class = ModelsIndexRedis
