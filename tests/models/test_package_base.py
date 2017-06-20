import pytest
import os
from appr.models.kv.etcd.package import Package as PackageEtcd
from appr.models.package_base import PackageBase


PACKAGE_CLASSES = ([PackageEtcd, PackageBase], ['appr.etcd', 'appr.base'])
@pytest.fixture(params=PACKAGE_CLASSES[0], ids=PACKAGE_CLASSES[1])
def package_class(request):
    return request.param

def test_package_init(package_class):
    p = package_class("titi/toot")
    assert p.name == "toot"
    assert p.namespace == "titi"
