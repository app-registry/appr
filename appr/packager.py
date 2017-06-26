import base64
import gzip
import hashlib
import logging
import tarfile
import io
import os

LOGGER = logging.getLogger(__name__)


def authorized_files():
    files = []
    for root, _, filenames in os.walk('.'):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def pack_app(app):
    tar = tarfile.open(app, "w:gz")
    for filename in authorized_files():
        tar.add(filename)
    tar.close()


def unpack_app(app, dest="."):
    tar = tarfile.open(app, "r:gz")
    tar.extractall(dest)
    tar.close()


# @TODO RENAME CLASS
class Package(object):
    def __init__(self, blob=None, b64_encoded=True):
        self.files = {}
        self.tar = None
        self.blob = None
        self.io_file = None
        self._digest = None
        self._size = None
        self.b64blob = None
        if blob is not None:
            self.load(blob, b64_encoded)

    def _load_blob(self, blob, b64_encoded):
        if b64_encoded:
            self.b64blob = blob
            self.blob = base64.b64decode(blob)
        else:
            self.b64blob = base64.b64encode(blob)
            self.blob = blob

    def load(self, blob, b64_encoded=True):
        self._digest = None
        self._load_blob(blob, b64_encoded)
        self.io_file = io.BytesIO(self.blob)
        self.tar = tarfile.open(fileobj=self.io_file, mode='r:gz')
        for member in self.tar.getmembers():
            tfile = self.tar.extractfile(member)
            if tfile is not None:
                self.files[tfile.name] = tfile.read()

    def extract(self, dest):
        self.tar.extractall(dest)

    def pack(self, dest):
        with open(dest, "wb") as destfile:
            destfile.write(self.blob)

    def tree(self, directory=None):
        files = self.files.keys()
        files.sort()
        if directory is not None:
            filtered = [x for x in files if x.startswith(directory)]
        else:
            filtered = files
        return filtered

    def file(self, filename):
        return self.files[filename]

    @property
    def size(self):
        if self._size is None:
            self.io_file.seek(0, os.SEEK_END)
            self._size = self.io_file.tell()
        return self._size

    @property
    def digest(self):
        if self._digest is None:
            self.io_file.seek(0)
            gunzip = gzip.GzipFile(fileobj=self.io_file, mode='r').read()
            self._digest = hashlib.sha256(gunzip).hexdigest()
            self.io_file.seek(0)
        return self._digest
