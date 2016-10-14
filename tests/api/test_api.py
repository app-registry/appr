import pytest
from cnr.tests.test_apiserver import BaseTestServer, LiveTestServer




@pytest.mark.redis
class TestLiveServerRedis(LiveTestServer):
    from cnr.models.kv.redis.db import RedisDB
    DB_CLASS = RedisDB


@pytest.mark.etcd
class TestLiveServerEtcd(LiveTestServer):
    from cnr.models.kv.etcd.db import EtcdDB
    DB_CLASS = EtcdDB


@pytest.mark.redis
class TestServerRedis(BaseTestServer):
    from cnr.models.kv.redis.db import RedisDB
    DB_CLASS = RedisDB


@pytest.mark.etcd
class TestServerEtcd(BaseTestServer):
    from cnr.models.kv.etcd.db import EtcdDB
    DB_CLASS = EtcdDB



@pytest.mark.filesystem
class TestLiveServerFilesystem(LiveTestServer):
    from cnr.models.kv.filesystem.db import FilesystemDB
    DB_CLASS = FilesystemDB


@pytest.mark.filesystem
class TestServerFilesystem(BaseTestServer):
    from cnr.models.kv.filesystem.db import FilesystemDB
    DB_CLASS = FilesystemDB
