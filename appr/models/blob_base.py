from __future__ import absolute_import, division, print_function

import appr.pack as packager

DEFAULT_MEDIA_TYPE = 'kpm'


class BlobBase(object):
    def __init__(self, package_name, blob, b64_encoded=True):
        self.package = package_name
        self.packager = packager.ApprPackage(blob, b64_encoded)

    @classmethod
    def get(cls, package_name, digest):
        b64blob = cls._fetch_b64blob(package_name, digest)
        return cls(package_name, b64blob)

    def save(self, content_media_type):
        raise NotImplementedError

    @classmethod
    def delete(cls, package_name, digest):
        raise NotImplementedError

    @classmethod
    def _fetch_b64blob(cls, package_name, digest):
        raise NotImplementedError

    @property
    def b64blob(self):
        return self.packager.b64blob

    @property
    def blob(self):
        return self.packager.blob

    @property
    def digest(self):
        return self.packager.digest

    @property
    def size(self):
        return self.packager.size
