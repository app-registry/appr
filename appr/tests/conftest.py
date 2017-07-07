from __future__ import absolute_import, division, print_function

import json
import os

import pytest

from appr.utils import symbol_by_name

LOCAL_DIR = os.path.dirname(__file__)


@pytest.fixture()
def data_dir():
    return LOCAL_DIR + "/data"


@pytest.fixture
def discovery_html():
    return """<html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="appr-package" content="appr.sh/{name} https://api.kubespray.io/api/v1/packages/{name}/pull">
    </head>
    <body>
    <a href=https://github.com/coreos/appr>coreos/appr</a>
    </body>
    </html>"""


@pytest.fixture
def app(db_class):
    create_app = symbol_by_name(os.getenv("APPR_FLASK_APP", "appr.api.app:create_app"))
    app = create_app()
    return app


@pytest.fixture()
def api_prefix():
    return os.getenv("APPR_API_PREFIX", "")


@pytest.fixture()
def fake_home(monkeypatch, tmpdir):
    home = tmpdir.mkdir('home')
    monkeypatch.setenv("HOME", home)
    return home


def get_response(name, kind):
    f = open(LOCAL_DIR + "/data/responses/%s-%s.json" % (name, kind))
    r = f.read()
    f.close()
    return r


@pytest.fixture(scope="module")
def kubeui_package():
    import base64
    import appr.pack
    with open(LOCAL_DIR + "/data/kube-ui.tar.gz", "rb") as f:
        package = appr.pack.ApprPackage(base64.b64encode(f.read()))
    return package


@pytest.fixture(scope='module')
def package_b64blob():
    return """\
H4sICF8BsVcC/3RpdF9yb2NrZXRjaGF0XzEuMTAuMGt1Yi50YXIA7Zddb9MwFIZ7nV9hlYve0DRpmgZFgJjGhCat2zQGNwhNXup1Vu04st\
1IVZX/znGTtMnYWAWj08DPRT6Ofezjr/ckF0cHHydHLp92/h4eMB6PzN2PQq95L4lGHX84HkfjcBz4YPeDKPA6yOvsgYXSWCLUwYzMJE4fn\
IfHyquhbO4vBEeKZE50cou1826L47xCxylMDWOOM884ouULalR3OpYXD8cpvSFKu0vM2fOcf98LAjj/URgE/ggK4PyHPpjs+d8D/X7fyXAy\
xzMSOwilmJMYdTXVg+1J70IBXuhbIWN0kGpBU4JOytlAb4faxaXtw4xjytxE8PfgkBOpqEhj5Lu+53pgmRKVSJrptbWhIwgxmpBUQceT40v\
HybGk+JoRZQKSJINSrKAdeKPcxNlwrqJ0zXPMsIadXI1CwajInX5MfFcLyWKkuM7iwQBsCYMdQGBk1YPLRIKZqSzSmZhel/WrF3CpntzVat\
NLUbgqT8BSNVEU8TCCLT5oiqUkSixkUo6qj24oa0XXNy0suem4XoVW6AjpZQZGqObc34DcyV+C+xTmVCzLOMqqoPCuuh3AQgZ+PUIr7/8Dm\
vBsfW4GP22lvel/4Jnvv8gLQ89cQP+jyB9a/d+X/uOMfq3VOvedOU2nMboohdeo9aFItRSMEelwovEUa7zNFW0hx9eEgVavevM3qo+zrBej\
3rZG7zXqVXnBFOR+r2irdUtUHZWRpJ0DVqv6uTCeijCSaJOWHurQ1Kq3eLyWweYIDL8VMnRdxWZIYH4wJECpakv/fgk27JjCSlpJo4ZRTnX\
LAiFkC8iQnsdbVk64kMsYBZ43oZsSkuZN5zrWydnpp7OrLxcnrSZyzBbrhWmkw6K4z/3g+OQX3lXmbbhmQsIo0LdVL5NCi0QwM8GXh+dmyj\
dTeg61eusReGA2Xd1d4e82UT21/lffIk+q/6OH//9Hw9D8/0ejcBSGQ7AP4Z9gbPX/OfS/m/vdKgN0PxOZw5d5909VfyeR31HL1x+xp2JKj\
DA4j6gIrOyM6EclBKzZto4VFIvFYrFYLBaLxWKxWCwWi8Xyb/ADcPSUWQAoAAA="""


@pytest.fixture(scope="module")
def kubeui_blob():
    with open(LOCAL_DIR + "/data/kube-ui.tar.gz", "rb") as f:
        package = f.read()
    return package


@pytest.fixture()
def package_dir(monkeypatch):
    monkeypatch.chdir(LOCAL_DIR + "/data/kube-ui")


@pytest.fixture()
def bad_package_dir(monkeypatch):
    monkeypatch.chdir(LOCAL_DIR + "/data/bad_manifest")


@pytest.fixture()
def empty_package_dir(monkeypatch):
    monkeypatch.chdir(LOCAL_DIR + "/data")


@pytest.fixture()
def pack_tar(package_dir, tmpdir):
    from appr.packager import pack_app
    kub = os.path.join(str(tmpdir.mkdir("tars")), "kube-ui.tar.gz")
    pack_app(kub)
    return kub


@pytest.fixture(scope="module")
def deploy_json():
    f = open(LOCAL_DIR + "/data/kube-ui_release.json", 'r')
    r = f.read()
    f.close()
    return r


@pytest.fixture(scope="module")
def deploy(deploy_json):
    return json.loads(deploy_json)


@pytest.fixture(scope="module")
def ns_resource(deploy):
    kubeui = deploy["deploy"][0]
    return kubeui['resources'][0]


@pytest.fixture(scope="module")
def rc_resource(deploy):
    kubeui = deploy["deploy"][0]
    return kubeui['resources'][1]


@pytest.fixture(scope="module")
def svc_resource(deploy):
    kubeui = deploy["deploy"][0]
    return kubeui['resources'][2]


@pytest.fixture(scope="session")
def db_names():
    return os.getenv("APPR_TEST_DB", "filesystem,redis,etcd").replace(r" ", "").split(",")


def get_db_classes():
    class_names = os.getenv("APPR_DB_CLASSES", "appr.models.kv.etcd.db:EtcdDB,\
                            appr.models.kv.filesystem.db:FilesystemDB,\
                            appr.models.kv.redis.db:RedisDB").replace(r" ", "").split(",")
    return [symbol_by_name(symbol) for symbol in class_names]


DB_CLASSES = get_db_classes()
PACKAGE_CLASSES = [dbc.Package for dbc in DB_CLASSES]
CHANNEL_CLASSES = [dbc.Channel for dbc in DB_CLASSES]


def class_name(obj):
    return "%s:%s" % (obj.__module__, obj.__name__)


@pytest.fixture()
def kv_prefix(monkeypatch):
    monkeypatch.setattr('appr.models.kv.APPR_KV_PREFIX', "appr-tests/packages/")
    monkeypatch.setenv("APPR_KV_PREFIX", "appr-tests/packages/")


@pytest.fixture()
def db():
    from appr.models.db_base import ApprDB
    return ApprDB


@pytest.fixture(scope='session')
def dbdata1():
    with open(LOCAL_DIR + "/data/backup1.json", "rb") as f:
        data = json.loads(f.read())
    return data


@pytest.fixture()
def db_class(db, monkeypatch, kv_prefix):
    monkeypatch.setenv("APPR_DB_CLASS", class_name(db))
    monkeypatch.setattr('appr.models.ApprDB', db)
    monkeypatch.setattr('appr.models.Package', db.Package)
    monkeypatch.setattr('appr.models.Channel', db.Channel)
    monkeypatch.setattr('appr.models.Blob', db.Blob)
    monkeypatch.setattr('appr.api.registry.Package', db.Package)
    monkeypatch.setattr('appr.api.registry.Channel', db.Channel)
    monkeypatch.setattr('appr.api.registry.Blob', db.Blob)
    return db


@pytest.fixture()
def newdb(kv_prefix, db_class):
    db_class.reset_db(True)
    yield db_class
    db_class.reset_db(True)


@pytest.fixture()
def db_with_data1(newdb, dbdata1):
    newdb.restore_backup(dbdata1)
    return newdb
