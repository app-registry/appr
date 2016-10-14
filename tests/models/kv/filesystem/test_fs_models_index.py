import pytest
from cnr.models.kv.filesystem.package import Package
from cnr.models.kv.filesystem.blob import Blob
from cnr.exception import UnableToLockResource



def test_locked(monkeypatch, package_b64blob):
    def set(path, ttl):
        return False
    monkeypatch.setattr("cnr.models.kv.filesystem.filesystem_client.lockttl", set)
    monkeypatch.setattr("cnr.models.kv.models_index_base.ModelsIndexBase.get_lock.im_func.__defaults__", (3, 0.1))

    with pytest.raises(UnableToLockResource):
        p = Package('a/b', "1.0.1", 'kpm', Blob("a/b", package_b64blob))
        p.save()
