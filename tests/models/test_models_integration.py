import pytest
from appr.tests.test_models import ApprTestModels
from appr.tests.conftest import db_names



if 'redis' in db_names():
    class TestRedisModels(ApprTestModels):
        from appr.models.kv.redis.db import RedisDB
        DB_CLASS = RedisDB


if 'etcd' in db_names():
    class TestEtcdModels(ApprTestModels):
        from appr.models.kv.etcd.db import EtcdDB
        DB_CLASS = EtcdDB


if 'filesystem' in db_names():
    class TestFilesystemModels(ApprTestModels):
        from appr.models.kv.filesystem.db import FilesystemDB
        DB_CLASS = FilesystemDB
