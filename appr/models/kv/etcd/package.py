from __future__ import absolute_import, division, print_function

from appr.models.kv.etcd.models_index import ModelsIndexEtcd
from appr.models.kv.package_kv_base import PackageKvBase


class Package(PackageKvBase):
    index_class = ModelsIndexEtcd
