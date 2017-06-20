import os
from appr.utils import symbol_by_name

DEFAULT_MEDIA_TYPE = 'kpm'
DEFAULT_STORAGE_MODULE = "appr.models.kv.filesystem"
DEFAULT_DB_CLASS = "%s.db:ApprDB" % DEFAULT_STORAGE_MODULE
DEFAULT_BLOB_CLASS = "%s.blob:Blob" % DEFAULT_STORAGE_MODULE

ApprDB = symbol_by_name(os.getenv("APPR_DB_CLASS", DEFAULT_DB_CLASS))

Channel = ApprDB.Channel
Package = ApprDB.Package
Blob = ApprDB.Blob
