import json
import etcd
import pytest
from cnr.models.kv.etcd.package import Package
from cnr.models.kv.etcd.blob import Blob
from cnr.exception import (
    InvalidRelease,
    UnableToLockResource
    )



class MockEtcdResult(object):
    def __init__(self, path, data):
        self.path = path
        self.data = data

    @property
    def key(self):
        return self.path

    @property
    def value(self):
        return json.dumps(self.data)


class MockEtcdResults(object):
    def __init__(self, results):
        self.results = results

    @property
    def children(self):
        return [MockEtcdResult(x, 'value') for x in self.results]


def test_etcdkey():
    pass


@pytest.fixture()
def getreleases(monkeypatch):

    def read(path, recursive=True):
        releases = ['1.3.0', '1.3.2-rc2', '1.8.2-rc2', '1.4.2', '1.0.0', '1.2.0']
        data = {'channels': {}, "releases": {}}
        for release in releases:
            data['releases'][release] = {"channels": [], "manifests": {"kpm": {"package": "titi/rocketchat", "created_at": "2016-10-11T12:03:24.941731", "blob": "H4sICHQ24VcC/2FudDMxX21vbmdvZGJfMS4wLjBrdWIudGFyAO2XX2vbMBDA86xPIbpBXhb/SZx4mG2sdGUUllG6spexB9VWUhHJMpJsCCXffac4duKSNdtYU0r1e5F91ulOsu5OEiRnM6qNtySC9x6HAJhMItuG8TjYbdeMR6NeOIwncTweTaJhLwhHURz1cNA7AqU2RGHcI7kZhQ/0O/R9M5e2fSYMBgNUkHRB5jRBGOdE0ASv5+oLmc9ldgNSUppbqRJ8mhvJcoq/0LkieYbfDY1HatnHuSCMe6kUH0ChokozmSc49AIvAEFGdapYYdbC7cCcpTTXYHF6cY1QRRQjN5xq6wkT1qW6bzLyhuthrHsa3IUPGZ2RkhuEFNWyVGmtNcAzxmlrYqCrdL2z4VMzua11jM2yAAl0Qnt01R+oKtDMaMHlsrZe93utKZ+hZ/H/r85PP03PPZE9oo1D8R9CuHTjfziMYhf/xwC1kSK5RO+3IPQKX+SwOJwjtCgEZvUL7iignuNZY6goODFU+/dT5vHiP4om9+J/EgZjF//Hqv+kYN+bgn1ShSdowfIMHr9RVUGBPkGCGpIRQ7YnhG0l3CnJd3fty2plqzu5oVyDvL94qwekKPoJ7jfbDFrZf4P7m6OC/VSF/RXSBU2tHSihNDX21PF7dWukrsNfZUYvpTIgKKABoz/u+oWSRqaSW73rs0trDf71nBrbE4TDGPYhCK3XO2PbfsVOj9VP9JLiX/3v8D8U/+EIAqsb/+M4DFz8P0X8V+Em+q/gVMtSYk/sZzI3SnJO1ZNkAlV7Aurh3+SFzcZO1qf1Xb8t/+SQVWycsqSwLgTuPko3ksGei4Jl72WmpnN9aeBMMNORgLWihBWArSU6YkGFVMsER59ZK68kLwWdyjLfZEJhHy+JubVz8e1C+HWeu5/6INc1gzyYR9upH0il7Xi1S/V4t1I3zsDgjVfb1fRV6nd2kL/7Z3wlpZnpdhar/Wbd0c7hcDgcDofD4XA4HA6Hw+FwOBwvmF+g+sIOACgAAA==", "release": release, "media_type": "kpm", "digest": "d3b54b7912fe770a61b59ab612a442eac52a8a5d8d05dbe92bf8f212d68aaa80"}}}
        assert path == "cnr/packages/ant31/rocketchat/releases.json"
        return MockEtcdResult(path, data)
    monkeypatch.setattr("cnr.models.kv.etcd.etcd_client.read", read)


def test_getreleases(getreleases):
    assert sorted(Package.all_releases("ant31/rocketchat")) == sorted(['1.3.0', '1.3.2-rc2', '1.8.2-rc2', '1.4.2', '1.0.0', '1.2.0'])


def test_getreleases_empty(monkeypatch):
    def read(path, recursive=True):
        assert path == "cnr/packages/ant31/rocketchat/releases.json"
        data = {'channels': {}, "releases": {}}
        return MockEtcdResult(path, data)
    monkeypatch.setattr("cnr.models.kv.etcd.etcd_client.read", read)
    assert Package.all_releases("ant31/rocketchat") == []


def test_getrelease_default(getreleases):
    assert str(Package.get_release("ant31/rocketchat", "default")) == "1.8.2-rc2"


def test_getrelease_stable_none(getreleases):
    assert str(Package.get_release("ant31/rocketchat", None, True)) == "1.4.2"


def test_getrelease_invalid(getreleases):
    with pytest.raises(InvalidRelease):
        str(Package.get_release("ant31/rocketchat", "==4.25a"))


def test_getrelease_prerelease(getreleases):
    str(Package.get_release("ant31/rocketchat", ">=0-")) == "1.8.2-rc2"


def test_locked(monkeypatch, package_b64blob):

    def write(path, data, prevExist, ttl=None):
        raise etcd.EtcdAlreadyExist

    def read(path):
        assert path == ""
        return True
    monkeypatch.setattr("cnr.models.kv.models_index_base.ModelsIndexBase.get_lock.im_func.__defaults__", (3, 0.1))

    monkeypatch.setattr("cnr.models.kv.etcd.etcd_client.read", read)
    monkeypatch.setattr("cnr.models.kv.etcd.etcd_client.write", write)
    with pytest.raises(UnableToLockResource):
        p = Package('a/b', "1.0.1", 'kpm', Blob("a/b", package_b64blob))
        p.save()
