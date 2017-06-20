from cnr.models.kv.blob_kv_base import BlobKvBase
from cnr.models.kv.redis.models_index import ModelsIndexRedis


class Blob(BlobKvBase):
    index_class = ModelsIndexRedis
