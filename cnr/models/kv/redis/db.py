import os

from cnr.exception import Forbidden

from cnr.models.db_base import CnrDB
from cnr.models.kv.redis import redis_client
from cnr.models.kv.redis.package import Package
from cnr.models.kv.redis.channel import Channel
from cnr.models.kv.redis.blob import Blob


class RedisDB(CnrDB):
    Channel = Channel
    Package = Package
    Blob = Blob

    # @TODO reset only key with prefix
    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("CNR_DB_ALLOW_RESET", "false") == "true" or force:
            redis_client.flushall()
        else:
            raise Forbidden("Reset DB is deactivated")


CnrDB = RedisDB
