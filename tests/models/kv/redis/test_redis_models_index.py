from __future__ import absolute_import, division, print_function

import pytest

from appr.exception import UnableToLockResource
from appr.models.kv.redis.blob import Blob
from appr.models.kv.redis.package import Package


def test_locked(monkeypatch, package_b64blob):
    def set(path, data, nx, ex):
        return None
    monkeypatch.setattr("appr.models.kv.redis.redis_client.set", set)
    monkeypatch.setattr("appr.models.kv.models_index_base.ModelsIndexBase.get_lock.im_func.__defaults__", (3, 0.1))

    with pytest.raises(UnableToLockResource):
        p = Package('a/b', "1.0.1", 'kpm', Blob("a/b", package_b64blob))
        p.save()
