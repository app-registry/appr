import os
from cnr.utils import symbol_by_name

DEFAULT_MEDIA_TYPE = 'kpm'
DEFAULT_STORAGE_MODULE = "cnr.models.kv.filesystem"
DEFAULT_DB_CLASS = "%s.db:CnrDB" % DEFAULT_STORAGE_MODULE
DEFAULT_BLOB_CLASS = "%s.blob:Blob" % DEFAULT_STORAGE_MODULE

CnrDB = symbol_by_name(os.getenv("CNR_DB_CLASS", DEFAULT_DB_CLASS))

Channel = CnrDB.Channel
Package = CnrDB.Package
Blob = CnrDB.Blob
