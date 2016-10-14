import pytest
import os
from cnr.models.kv.etcd.package import Package as PackageEtcd
from cnr.models.package_base import PackageBase


PACKAGE_CLASSES = ([PackageEtcd, PackageBase], ['cnr.etcd', 'cnr.base'])
@pytest.fixture(params=PACKAGE_CLASSES[0], ids=PACKAGE_CLASSES[1])
def package_class(request):
    return request.param

def test_package_init(package_class):
    p = package_class("titi/toot")
    assert p.name == "toot"
    assert p.namespace == "titi"
