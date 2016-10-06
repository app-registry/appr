import pytest
from cnr.tests.apiserver import BaseTestServer, LiveTestServer


@pytest.mark.redis
class TestLiveTestServerRedis(LiveTestServer):
    from cnr.models.kv.redis.db import RedisDB
    DB_CLASS = RedisDB


@pytest.mark.redis
class TestServerRedis(BaseTestServer):
    from cnr.models.kv.redis.db import RedisDB
    DB_CLASS = RedisDB


@pytest.mark.etcd
class TestServerEtcd(BaseTestServer):
    from cnr.models.kv.etcd.db import EtcdDB
    DB_CLASS = EtcdDB


@pytest.mark.etcd
class TestLiveTestServerEtcd(LiveTestServer):
    from cnr.models.kv.etcd.db import EtcdDB
    DB_CLASS = EtcdDB


@pytest.mark.filesystem
class TestServerFilesystem(BaseTestServer):
    from cnr.models.kv.filesystem.db import FilesystemDB
    DB_CLASS = FilesystemDB


@pytest.mark.filesystem
class TestLiveTestServerFilesystem(LiveTestServer):
    from cnr.models.kv.filesystem.db import FilesystemDB
    DB_CLASS = FilesystemDB
