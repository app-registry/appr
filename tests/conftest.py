from __future__ import absolute_import, division, print_function
import os.path
import base64
import json

import pytest

from appr.commands.cli import all_commands, get_parser
from appr.tests.conftest import (api_prefix, app, bad_package_dir, class_name,
                                 data_dir, db, db_class, db_names,
                                 db_with_data1, dbdata1, deploy,
                                 discovery_html, empty_package_dir, fake_home,
                                 get_db_classes, get_response, kubeui_blob,
                                 kubeui_package, kv_prefix, newdb, ns_resource,
                                 pack_tar, package_b64blob, package_dir,
                                 rc_resource, svc_resource)

LOCAL_DIR = os.path.dirname(__file__)


@pytest.fixture()
def plugin_helm_tarball():
    with open(os.path.join(LOCAL_DIR, "data/plugins/appr-helm-plugin-v0.5.1.tar.gz"), "rb") as f:
        return f.read()


@pytest.fixture()
def plugin_helm_releases():
    with open(os.path.join(LOCAL_DIR, "data/plugins/github-tags-helm-plugin.json"), "rb") as f:
        return f.read()


@pytest.fixture()
def cli_parser():
    return get_parser(all_commands())


@pytest.fixture(scope='module')
def package_blob(package_b64blob):
    return base64.b64decode(package_b64blob)


@pytest.fixture(scope='module')
def package_data():
    return b'H4sICF8BsVcC/3RpdF9yb2NrZXRjaGF0XzEuMTAuMGt1Yi50YXIA7Zddb9MwFIZ7nV9hlYve0DRpmgZFgJjGhCat2zQGNwhNXup1Vu04st1IVZX/znGTtMnYWAWj08DPRT6Ofezjr/ckF0cHHydHLp92/h4eMB6PzN2PQq95L4lGHX84HkfjcBz4YPeDKPA6yOvsgYXSWCLUwYzMJE4fnIfHyquhbO4vBEeKZE50cou1826L47xCxylMDWOOM884ouULalR3OpYXD8cpvSFKu0vM2fOcf98LAjj/URgE/ggK4PyHPpjs+d8D/X7fyXAyxzMSOwilmJMYdTXVg+1J70IBXuhbIWN0kGpBU4JOytlAb4faxaXtw4xjytxE8PfgkBOpqEhj5Lu+53pgmRKVSJrptbWhIwgxmpBUQceT40vHybGk+JoRZQKSJINSrKAdeKPcxNlwrqJ0zXPMsIadXI1CwajInX5MfFcLyWKkuM7iwQBsCYMdQGBk1YPLRIKZqSzSmZhel/WrF3CpntzVatNLUbgqT8BSNVEU8TCCLT5oiqUkSixkUo6qj24oa0XXNy0suem4XoVW6AjpZQZGqObc34DcyV+C+xTmVCzLOMqqoPCuuh3AQgZ+PUIr7/8DmvBsfW4GP22lvel/4Jnvv8gLQ89cQP+jyB9a/d+X/uOMfq3VOvedOU2nMboohdeo9aFItRSMEelwovEUa7zNFW0hx9eEgVavevM3qo+zrBej3rZG7zXqVXnBFOR+r2irdUtUHZWRpJ0DVqv6uTCeijCSaJOWHurQ1Kq3eLyWweYIDL8VMnRdxWZIYH4wJECpakv/fgk27JjCSlpJo4ZRTnXLAiFkC8iQnsdbVk64kMsYBZ43oZsSkuZN5zrWydnpp7OrLxcnrclientSZyzBbrhWmkw6K4z/3g+OQX3lXmbbhmQsIo0LdVL5NCi0QwM8GXh+dmyjdTeg61eusReGA2Xd1d4e82UT21/lffIk+q/6OH//9Hw9D8/0ejcBSGQ7AP4Z9gbPX/OfS/m/vdKgN0PxOZw5d5909VfyeR31HL1x+xp2JKjDA4j6gIrOyM6EclBKzZto4VFIvFYrFYLBaLxWKxWCwWi8Xyb/ADcPSUWQAoAAA='
