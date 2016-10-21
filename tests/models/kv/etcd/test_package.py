import json
import pytest
import etcd
from cnr.models.kv.etcd.package import Package
from cnr.exception import (
    InvalidRelease,
    UnableToLockResource,
    PackageAlreadyExists
    )

@pytest.fixture()
def release_data():
    releases = ['1.3.0', '1.3.2-rc2', '1.8.2-rc2', '1.4.2', '1.0.0', '1.2.0']
    data = {'channels': {}, "releases": {}}
    for release in releases:
        data['releases'][release] = {"channels": [], "manifests": {"kpm": {"package": "titi/rocketchat", "created_at": "2016-10-11T12:03:24.941731", "blob": "H4sICHQ24VcC/2FudDMxX21vbmdvZGJfMS4wLjBrdWIudGFyAO2XX2vbMBDA86xPIbpBXhb/SZx4mG2sdGUUllG6spexB9VWUhHJMpJsCCXffac4duKSNdtYU0r1e5F91ulOsu5OEiRnM6qNtySC9x6HAJhMItuG8TjYbdeMR6NeOIwncTweTaJhLwhHURz1cNA7AqU2RGHcI7kZhQ/0O/R9M5e2fSYMBgNUkHRB5jRBGOdE0ASv5+oLmc9ldgNSUppbqRJ8mhvJcoq/0LkieYbfDY1HatnHuSCMe6kUH0ChokozmSc49AIvAEFGdapYYdbC7cCcpTTXYHF6cY1QRRQjN5xq6wkT1qW6bzLyhuthrHsa3IUPGZ2RkhuEFNWyVGmtNcAzxmlrYqCrdL2z4VMzua11jM2yAAl0Qnt01R+oKtDMaMHlsrZe93utKZ+hZ/H/r85PP03PPZE9oo1D8R9CuHTjfziMYhf/xwC1kSK5RO+3IPQKX+SwOJwjtCgEZvUL7iignuNZY6goODFU+/dT5vHiP4om9+J/EgZjF//Hqv+kYN+bgn1ShSdowfIMHr9RVUGBPkGCGpIRQ7YnhG0l3CnJd3fty2plqzu5oVyDvL94qwekKPoJ7jfbDFrZf4P7m6OC/VSF/RXSBU2tHSihNDX21PF7dWukrsNfZUYvpTIgKKABoz/u+oWSRqaSW73rs0trDf71nBrbE4TDGPYhCK3XO2PbfsVOj9VP9JLiX/3v8D8U/+EIAqsb/+M4DFz8P0X8V+Em+q/gVMtSYk/sZzI3SnJO1ZNkAlV7Aurh3+SFzcZO1qf1Xb8t/+SQVWycsqSwLgTuPko3ksGei4Jl72WmpnN9aeBMMNORgLWihBWArSU6YkGFVMsER59ZK68kLwWdyjLfZEJhHy+JubVz8e1C+HWeu5/6INc1gzyYR9upH0il7Xi1S/V4t1I3zsDgjVfb1fRV6nd2kL/7Z3wlpZnpdhar/Wbd0c7hcDgcDofD4XA4HA6Hw+FwOBwvmF+g+sIOACgAAA==", "release": release, "media_type": "kpm", "digest": "d3b54b7912fe770a61b59ab612a442eac52a8a5d8d05dbe92bf8f212d68aaa80"}}}
    return data

def test_check_data_validrelease():
    assert Package.check_release("1.4.5-alpha") is None


def test_check_data_invalidrelease():
    with pytest.raises(InvalidRelease):
        assert Package.check_release("1.4.5a-alpha")

# def test_push_etcd(monkeypatch, release_data, package_b64blob):
#     def write(path, data, prevExist=None, ttl=None):
#         assert path in ["cnr-tests/packages/a/b/releases.json",
#                         "cnr-tests/packages/a/b/releases.json.lock",
#                         'cnr-tests/packages/packages.json',
#                         'cnr-tests/packages/packages.json.lock']
#         if path == "cnr-tests/packages/a/b/releases.json.lock":
#             assert data == 'lock'
#         if path == "cnr-tests/packages/a/b/releases.json":
#             assert '4.3.0' in json.loads(data)['releases']
#         if path == "cnr-tests/packages/packages.json":
#             d = json.loads(data)
#             assert 'a' in d['packages'] and 'b' in d['packages']['a']
#         return True
#     monkeypatch.setattr("cnr.models.kv.etcd.etcd_client.write", write)
#     p = Package('a/b', '4.3.0', 'kpm', package_b64blob)
#     p.save()
