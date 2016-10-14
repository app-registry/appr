import pytest
from cnr.tests.test_models import CnrTestModels


@pytest.mark.redis
class TestRedisModels(CnrTestModels):
    from cnr.models.kv.redis.db import RedisDB
    DB_CLASS = RedisDB


@pytest.mark.etcd
class TestEtcdModels(CnrTestModels):
    from cnr.models.kv.etcd.db import EtcdDB
    DB_CLASS = EtcdDB


@pytest.mark.filesystem
class TestFilesystemModels(CnrTestModels):
    from cnr.models.kv.filesystem.db import FilesystemDB
    DB_CLASS = FilesystemDB
