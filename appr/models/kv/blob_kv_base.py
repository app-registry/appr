from __future__ import absolute_import, division, print_function

from appr.models.blob_base import BlobBase
from appr.models.kv.models_index_base import ModelsIndexBase


class BlobKvBase(BlobBase):
    index_class = ModelsIndexBase

    @property
    def index(self):
        return self.index_class(self.package)

    @classmethod
    def _fetch_b64blob(cls, package_name, digest):
        return cls.index_class(package_name).get_blob(digest)

    def save(self, content_media_type):
        return self.index.add_blob(self.b64blob, self.digest)

    @classmethod
    def delete(cls, package_name, digest):
        return cls.index_class(package_name).delete_blob(digest)
