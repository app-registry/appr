from __future__ import absolute_import, division, print_function

import os

from appr.exception import Forbidden
from appr.models.db_base import ApprDB
from appr.models.kv.redis import redis_client
from appr.models.kv.redis.blob import Blob
from appr.models.kv.redis.channel import Channel
from appr.models.kv.redis.package import Package


class RedisDB(ApprDB):
    Channel = Channel
    Package = Package
    Blob = Blob

    # @TODO reset only key with prefix
    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("APPR_DB_ALLOW_RESET", "false") == "true" or force:
            redis_client.flushall()
        else:
            raise Forbidden("Reset DB is deactivated")


ApprDB = RedisDB
