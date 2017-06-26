import os
import etcd

from appr.exception import Forbidden

from appr.models.db_base import ApprDB
import appr.models.kv
from appr.models.kv.etcd import etcd_client
from appr.models.kv.etcd.package import Package
from appr.models.kv.etcd.channel import Channel
from appr.models.kv.etcd.blob import Blob


class EtcdDB(ApprDB):
    Channel = Channel
    Package = Package
    Blob = Blob

    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("APPR_DB_ALLOW_RESET", "false") == "true" or force:
            try:
                etcd_client.delete(appr.models.kv.APPR_KV_PREFIX, recursive=True)
            except etcd.EtcdKeyNotFound:
                pass
        else:
            raise Forbidden("Reset DB is deactivated")


ApprDB = EtcdDB
