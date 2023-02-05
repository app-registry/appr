from __future__ import absolute_import, division, print_function

import pytest

from appr.tests.conftest import db_names
from appr.tests.test_models import ApprTestModels

class TestRedisModels(ApprTestModels):
        from appr.models.kv.redis.db import RedisDB
        DB_CLASS = RedisDB



class TestEtcdModels(ApprTestModels):
        from appr.models.kv.etcd.db import EtcdDB
        DB_CLASS = EtcdDB



class TestFilesystemModels(ApprTestModels):
        from appr.models.kv.filesystem.db import FilesystemDB
        DB_CLASS = FilesystemDB
