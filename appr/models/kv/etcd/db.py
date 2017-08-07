from __future__ import absolute_import, division, print_function

import os

import etcd

import appr.models.kv
from appr.exception import Forbidden
from appr.models.db_base import ApprDB
from appr.models.kv.etcd import etcd_client
from appr.models.kv.etcd.blob import Blob
from appr.models.kv.etcd.channel import Channel
from appr.models.kv.etcd.package import Package


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
