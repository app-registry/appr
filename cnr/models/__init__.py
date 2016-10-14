import os
from cnr.utils import symbol_by_name

DEFAULT_MEDIA_TYPE = 'kpm'
DEFAULT_DB_CLASS = "cnr.models.kv.filesystem.db:FilesystemDB"
DEFAULT_BLOB_CLASS = "cnr.models.kv.filesystem.blob:Blob"

Blob = symbol_by_name(os.getenv("CNR_BLOB_CLASS", DEFAULT_BLOB_CLASS))

CnrDB = symbol_by_name(os.getenv("CNR_DB_CLASS", DEFAULT_DB_CLASS))
Channel = CnrDB.Channel
Package = CnrDB.Package
