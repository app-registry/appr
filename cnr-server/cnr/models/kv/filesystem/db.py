import os

from cnr.exception import Forbidden

from cnr.models.db_base import CnrDB
import cnr.models.kv
from cnr.models.kv.filesystem import filesystem_client
from cnr.models.kv.filesystem.package import Package
from cnr.models.kv.filesystem.channel import Channel
from cnr.models.kv.filesystem.blob import Blob


class FilesystemDB(CnrDB):
    Channel = Channel
    Package = Package
    Blob = Blob

    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("CNR_DB_ALLOW_RESET", "false") == "true" or force:
            filesystem_client.flushall(cnr.models.kv.CNR_KV_PREFIX)
        else:
            raise Forbidden("Reset DB is deactivated")


CnrDB = FilesystemDB
