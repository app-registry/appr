from __future__ import absolute_import, division, print_function

from appr.models.kv.blob_kv_base import BlobKvBase
from appr.models.kv.redis.models_index import ModelsIndexRedis


class Blob(BlobKvBase):
    index_class = ModelsIndexRedis
