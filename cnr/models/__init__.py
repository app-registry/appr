import os
from cnr.utils import symbol_by_name


DEFAULT_DB_CLASS = "cnr.models.kv.etcd.db:EtcdDB"


CnrDB = symbol_by_name(os.getenv("CNR_DB_CLASS", DEFAULT_DB_CLASS))
Package = CnrDB.Package
Channel = CnrDB.Channel
