import os
import time
import shutil
from appr.utils import Singleton, mkdir_p


class FilesystemClient(object):
    __metaclass__ = Singleton

    def __init__(self, path):
        self.base_path = path

    def lockttl(self, key, ttl):
        if key[0] == "/":
            key = key[1:]
        path = os.path.join(self.base_path, key)
        expiration = 0.0
        if os.path.exists(path):
            with open(path, 'rb') as f:
                expiration = float(f.read())
        if time.time() >= expiration:
            next_expiration = time.time() + ttl
            return self.set(key, str(next_expiration), None)
        return False

    def set(self, key, data, nx=None):
        if key[0] == "/":
            key = key[1:]
        path = os.path.join(self.base_path, key)
        if nx is False and os.path.exists(path):
            return None
        mkdir_p(os.path.dirname(path))
        with open(path, 'wb') as f:
            f.write(data)
        return True

    def get(self, key):
        path = os.path.join(self.base_path, key)
        if not os.path.exists(path):
            return None
        with open(path, 'rb') as f:
            return f.read()

    def delete(self, key):
        path = os.path.join(self.base_path, key)
        if not os.path.exists(path):
            return None
        return os.remove(path)

    def flushall(self, root):
        if root[0] == "/":
            root = root[1:]
        path = os.path.join(self.base_path, root)
        if os.path.exists(path):
            shutil.rmtree(path)


BASE_PATH = os.getenv('DATABASE_URL', "/tmp/appr")
filesystem_client = FilesystemClient(BASE_PATH)
