import time

import cnr.models.kv
from cnr.models.kv.models_index_base import ModelsIndexBase
from cnr.models.kv.redis import redis_client
from cnr.exception import (UnableToLockResource,
                           ResourceNotFound)


class ModelsIndexRedis(ModelsIndexBase):
    def _fetch_raw_data(self, path):
        path = cnr.models.kv.CNR_KV_PREFIX + path
        datablob = redis_client.get(path)
        if datablob is None:
            raise ResourceNotFound("resource %s not found" % path, {"path": path})
        package_data = datablob
        return package_data

    def _write_raw_data(self, key, data):
        path = cnr.models.kv.CNR_KV_PREFIX + key
        redis_client.set(path, data)

    def _delete_data(self, key):
        path = cnr.models.kv.CNR_KV_PREFIX + key
        return redis_client.delete(path) == 1

    def _get_lock(self, lock_key, ttl=3, timeout=4):
        if timeout is not None:
            timeout_time = time.time() + timeout   # 5 minutes from now
        while True:
            if redis_client.set(lock_key, 'locked', nx=True, ex=ttl):
                return True
            else:
                if timeout is None or time.time() > timeout_time:
                    raise UnableToLockResource("%s already locked" % lock_key, {"lock_key": lock_key, "ttl": ttl})
                else:
                    time.sleep(0.2)

    def _lock_key(self, key):
        return "%s%s.lock" % (cnr.models.kv.CNR_KV_PREFIX, key)

    def _release_lock(self, lock_key):
        redis_client.delete(lock_key)
