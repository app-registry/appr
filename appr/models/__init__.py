import os
from appr.utils import symbol_by_name

DEFAULT_MEDIA_TYPE = 'kpm'
DEFAULT_STORAGE_MODULE = "appr.models.kv.filesystem"
DEFAULT_DB_CLASS = "%s.db:ApprDB" % DEFAULT_STORAGE_MODULE
DEFAULT_BLOB_CLASS = "%s.blob:Blob" % DEFAULT_STORAGE_MODULE


def get_db_class(name=None):
    if not name:
        name = os.getenv("APPR_DB_CLASS", DEFAULT_DB_CLASS)

    if name == "filesystem":
        from appr.models.kv.filesystem.db import FilesystemDB
        db = FilesystemDB

    elif name == "redis":
        from appr.models.kv.redis.db import RedisDB
        db = RedisDB

    elif name == "etcd":
        from appr.models.kv.etcd.db import EtcdDB
        db = EtcdDB

    else:
        db = symbol_by_name(name)

    return db


ApprDB = get_db_class()
Channel = ApprDB.Channel
Package = ApprDB.Package
Blob = ApprDB.Blob
