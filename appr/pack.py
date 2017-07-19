from __future__ import absolute_import, division, print_function

import base64
import fnmatch
import glob
import gzip
import hashlib
import io
import os
import tarfile

AUTHORIZED_FILES = [
    "*.libsonnet", "*.libjsonnet", "*.jsonnet", "*.yaml", "README.md", "LICENSE", "AUTHORS",
    "NOTICE", "manifests", "deps/*.kub"]

AUTHORIZED_TEMPLATES = ["*.yaml", "*.jsonnet", "*.libjsonnet", "*.yml", "*.j2", "*.libsonnet"]


def authorized_files():
    files = []
    for name in AUTHORIZED_FILES:
        for filename in glob.glob(name):
            files.append(filename)
    for root, _, filenames in os.walk('templates'):
        for name in AUTHORIZED_TEMPLATES:
            for filename in fnmatch.filter(filenames, name):
                files.append(os.path.join(root, filename))
    return files


def all_files():
    files = []
    ignore_files = []
    for filename in ['.helmignore', '.apprignore', '.kpmignore']:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                ignore_files = ignore_files + f.read().split("\n")

    for root, _, filenames in os.walk('.'):
        for filename in filenames:
            path = os.path.join(root, filename)
            skip = False
            for ignore_pattern in ignore_files:
                if fnmatch.fnmatch(path, ignore_pattern):
                    skip = True
                    break
            if not skip:
                files.append(path.replace("./", ""))
    return files


def pack_kub(kub, filter_files=True, prefix=None):
    tar = tarfile.open(kub, "w:gz")
    if filter_files:
        files = authorized_files()
    else:
        files = all_files()
    for filepath in files:
        arcname = None
        if prefix:
            arcname = os.path.join(prefix, filepath)
        tar.add(filepath, arcname=arcname)

    tar.close()


def unpack_kub(kub, dest="."):
    tar = tarfile.open(kub, "r:gz")
    tar.extractall(dest)
    tar.close()


class ApprPackage(object):
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
        files = list(self.files.keys())
        files.sort()

        if directory is not None:
            filtered = [x for x in files if x.startswith(directory)]
        else:
            filtered = files
        return filtered

    def file(self, filename):
        return self.files[filename]

    @property
    def manifest(self):
        manifests_files = ["manifest.yaml", "manifest.jsonnet", "Chart.yaml", "Chart.yml"]
        for filename in manifests_files:
            if filename in self.files:
                return self.files[filename]
        raise RuntimeError("Unknown manifest format")

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
