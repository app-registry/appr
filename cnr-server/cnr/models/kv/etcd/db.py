import os
import etcd

from cnr.exception import Forbidden

from cnr.models.db_base import CnrDB
import cnr.models.kv
from cnr.models.kv.etcd import etcd_client
from cnr.models.kv.etcd.package import Package
from cnr.models.kv.etcd.channel import Channel
from cnr.models.kv.etcd.blob import Blob


class EtcdDB(CnrDB):
    Channel = Channel
    Package = Package
    Blob = Blob

    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("CNR_DB_ALLOW_RESET", "false") == "true" or force:
            try:
                etcd_client.delete(cnr.models.kv.CNR_KV_PREFIX, recursive=True)
            except etcd.EtcdKeyNotFound:
                pass
        else:
            raise Forbidden("Reset DB is deactivated")


CnrDB = EtcdDB
