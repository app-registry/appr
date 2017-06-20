from cnr.models.kv.blob_kv_base import BlobKvBase
from cnr.models.kv.etcd.models_index import ModelsIndexEtcd


class Blob(BlobKvBase):
    index_class = ModelsIndexEtcd
