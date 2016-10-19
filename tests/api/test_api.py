import pytest
from cnr.tests.test_apiserver import ServerTest
from cnr.tests.conftest import db_names


if 'redis' in db_names():
    class TestServerRedis(ServerTest):
        from cnr.models.kv.redis.db import RedisDB
        DB_CLASS = RedisDB


if 'etcd' in db_names():
    class TestServerEtcd(ServerTest):
        from cnr.models.kv.etcd.db import EtcdDB
        DB_CLASS = EtcdDB


if 'filesystem' in db_names():
    class TestServerFilesystem(ServerTest):
        from cnr.models.kv.filesystem.db import FilesystemDB
        DB_CLASS = FilesystemDB
