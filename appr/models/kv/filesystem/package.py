from __future__ import absolute_import, division, print_function

from appr.models.kv.filesystem.models_index import ModelsIndexFilesystem
from appr.models.kv.package_kv_base import PackageKvBase


class Package(PackageKvBase):
    index_class = ModelsIndexFilesystem
