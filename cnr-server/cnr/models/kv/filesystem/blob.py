from cnr.models.kv.blob_kv_base import BlobKvBase
from cnr.models.kv.filesystem.models_index import ModelsIndexFilesystem


class Blob(BlobKvBase):
    index_class = ModelsIndexFilesystem
