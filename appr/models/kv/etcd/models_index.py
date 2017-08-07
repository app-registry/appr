from __future__ import absolute_import, division, print_function

import time

import etcd

import appr.models.kv
from appr.exception import ResourceNotFound, UnableToLockResource
from appr.models.kv.etcd import etcd_client
from appr.models.kv.models_index_base import ModelsIndexBase


class ModelsIndexEtcd(ModelsIndexBase):
    def _fetch_raw_data(self, path):
        path = appr.models.kv.APPR_KV_PREFIX + path
        try:
            data = etcd_client.read(path).value
        except etcd.EtcdKeyError as excp:
            raise ResourceNotFound(excp.message, {"path": path})
        return data

    def _write_raw_data(self, key, data):
        path = appr.models.kv.APPR_KV_PREFIX + key
        etcd_client.write(path, data)

    def _delete_data(self, key):
        path = appr.models.kv.APPR_KV_PREFIX + key
        try:
            etcd_client.delete(path)
        except etcd.EtcdKeyError:
            pass

    def _get_lock(self, lock_key, ttl=3, timeout=4):
        if timeout is not None:
            timeout_time = time.time() + timeout  # 5 minutes from now
        while True:
            try:
                etcd_client.write(lock_key, 'lock', prevExist=False, ttl=ttl)
                return True
            except etcd.EtcdAlreadyExist:
                if timeout is None or time.time() > timeout_time:
                    raise UnableToLockResource("%s already locked" % lock_key, {
                        "lock_key": lock_key,
                        "ttl": ttl})
                else:
                    time.sleep(0.2)

    def _lock_key(self, key):
        return "%s%s.lock" % (appr.models.kv.APPR_KV_PREFIX, key)

    def _release_lock(self, lock_key):
        return self._delete_data(lock_key.replace(appr.models.kv.APPR_KV_PREFIX, ""))
