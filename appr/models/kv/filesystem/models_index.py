from __future__ import absolute_import, division, print_function

import time

import appr.models.kv
from appr.exception import ResourceNotFound, UnableToLockResource
from appr.models.kv.filesystem import filesystem_client
from appr.models.kv.models_index_base import ModelsIndexBase


class ModelsIndexFilesystem(ModelsIndexBase):
    def _fetch_raw_data(self, path):
        path = appr.models.kv.APPR_KV_PREFIX + path
        datablob = filesystem_client.get(path)
        if datablob is None:
            raise ResourceNotFound("resource %s not found" % path, {"path": path})
        package_data = datablob
        return package_data

    def _write_raw_data(self, key, data):
        path = appr.models.kv.APPR_KV_PREFIX + key
        filesystem_client.set(path, data)

    def _delete_data(self, key):
        path = appr.models.kv.APPR_KV_PREFIX + key
        return filesystem_client.delete(path)

    def _get_lock(self, lock_key, ttl=3, timeout=4):
        if timeout is not None:
            timeout_time = time.time() + timeout
        while True:
            if filesystem_client.lockttl(lock_key, ttl):
                return True
            else:
                if timeout is None or time.time() > timeout_time:
                    raise UnableToLockResource("%s already locked" % lock_key, {
                        "lock_key": lock_key,
                        "ttl": ttl})
                else:
                    time.sleep(0.2)

    def _lock_key(self, key):
        return "%s%s.lock" % (appr.models.kv.APPR_KV_PREFIX, key)

    def _release_lock(self, lock_key):
        filesystem_client.delete(lock_key)
