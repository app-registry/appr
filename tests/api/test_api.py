import pytest
from cnr.tests.test_apiserver import BaseTestServer, LiveTestServer
from cnr.tests.conftest import db_names


if 'redis' in db_names():
    class TestLiveServerRedis(LiveTestServer):
        from cnr.models.kv.redis.db import RedisDB
        DB_CLASS = RedisDB

    class TestServerRedis(BaseTestServer):
        from cnr.models.kv.redis.db import RedisDB
        DB_CLASS = RedisDB


if 'etcd' in db_names():
    class TestServerEtcd(BaseTestServer):
        from cnr.models.kv.etcd.db import EtcdDB
        DB_CLASS = EtcdDB


    class TestLiveServerEtcd(LiveTestServer):
        from cnr.models.kv.etcd.db import EtcdDB
        DB_CLASS = EtcdDB


if 'filesystem' in db_names():
    class TestLiveServerFilesystem(LiveTestServer):
        from cnr.models.kv.filesystem.db import FilesystemDB
        DB_CLASS = FilesystemDB


    class TestServerFilesystem(BaseTestServer):
        from cnr.models.kv.filesystem.db import FilesystemDB
        DB_CLASS = FilesystemDB
