from __future__ import absolute_import, division, print_function
import re

import pytest
from appr.display import print_packages, print_deploy_result


def _strip_spaces(string):
    s = re.sub(' +',' ', string)
    return re.sub('--+', '--', s)


@pytest.fixture()
def package_list():
    h = [{"name": "o1/p1",
          "default": "1.4.0",
          "downloads": 45,
          "manifests": ['kpm'],
          "releases": ["1.3.0", "1.2.0"]},
         {"name": "o1/p2",
          "default": "1.4.0",
          "manifests": ['kpm'],
          "downloads": 45,
          "releases": ["1.3.0", "1.2.0"]}]
    return h


@pytest.fixture()
def deploy_result():
    from collections import OrderedDict
    h = [OrderedDict([("package", "o1/p1"),
                      ("release", "1.4.0"),
                      ("type", "replicationcontroller"),
                      ("name", "p1"),
                      ("namespace", "testns"),
                      ("status", "ok")]).values(),
         OrderedDict([("package", "o1/p1"),
                      ("release", "1.4.0"),
                      ("type", "svc"),
                      ("name", "p1"),
                      ("namespace", "testns"),
                      ("status", "updated")]).values(),

         ]
    return h


def test_empty_list():
    out = print_packages([])
    res = unicode("\n".join(["app    release    downloads    manifests",
                     "-----  ---------  -----------  -----------"]))
    assert _strip_spaces(out) == _strip_spaces(res)


def test_print_packages(package_list):
    out = print_packages(package_list)
    res = unicode("\n".join(["app    release      downloads  manifests",
                             "-----  ---------  -----------  -----------",
                             "/o1/p1  1.4.0               45  kpm\n/o1/p2  1.4.0               45  kpm"]))

    assert _strip_spaces(out) == _strip_spaces(res)


def test_print_empty_deploy_result():
    out = print_deploy_result([])
    res = u'\n'.join(["package    release    type    name    namespace    status",
                      "---------  ---------  ------  ------  -----------  --------"])
    assert _strip_spaces(out) == _strip_spaces(res)


def test_print_deploy_result(deploy_result):
    out = print_deploy_result(deploy_result)
    res = "\n".join(["package    release    type                   name    namespace    status",
                     "---------  ---------  ---------------------  ------  -----------  --------",
                     "o1/p1      1.4.0      replicationcontroller  p1      testns       \x1b[32mok\x1b[0m",
                     "o1/p1      1.4.0      svc                    p1      testns       \x1b[36mupdated\x1b[0m"])

    assert _strip_spaces(out) == _strip_spaces(res)
