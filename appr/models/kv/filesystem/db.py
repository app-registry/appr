from __future__ import absolute_import, division, print_function

import os

import appr.models.kv
from appr.exception import Forbidden
from appr.models.db_base import ApprDB
from appr.models.kv.filesystem import filesystem_client
from appr.models.kv.filesystem.blob import Blob
from appr.models.kv.filesystem.channel import Channel
from appr.models.kv.filesystem.package import Package


class FilesystemDB(ApprDB):
    Channel = Channel
    Package = Package
    Blob = Blob

    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("APPR_DB_ALLOW_RESET", "false") == "true" or force:
            filesystem_client.flushall(appr.models.kv.APPR_KV_PREFIX)
        else:
            raise Forbidden("Reset DB is deactivated")


ApprDB = FilesystemDB
