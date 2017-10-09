from __future__ import absolute_import, division, print_function

import json
import os
import pytest
import requests_mock
import yaml

from appr.api.impl.registry import pull
from appr.client import DEFAULT_PREFIX, DEFAULT_REGISTRY
from appr.plugins.helm import Helm


def test_appr_dep(db_with_data1, tmpdir):
    version = '0.0.1'
    name = "titi/rocketchat"

    with requests_mock.mock() as m:
        response = pull(name, version, "helm", db_with_data1.Package, db_with_data1.Blob)
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/%s/%s/helm/pull" %
              (name, version), content=json.dumps(response))
        hp = Helm()
        tempdir = str(tmpdir.mkdir("charts"))
        deps = hp.download_appr_deps([{
            'name': "%s/%s" % (DEFAULT_REGISTRY, name),
            'version': version,
            'randomKey': 'oky'
        }], tempdir)
        sp = name.split("/")
        assert deps == [{
            "repository": "file://%s" % os.path.join(tempdir, sp[0], sp[1]),
            "version": '0.0.1',
            "name": 'rocketchat',
            "randomKey": 'oky'
        }]


@pytest.fixture
def chhome(fake_home, monkeypatch):
    monkeypatch.chdir(fake_home)


@pytest.mark.parametrize("req,expected", [
    ({
         'dependencies': []
     }, 'No appr-registries dependencies'),
    ({
         'dependencies': [],
         'appr': []
     }, 'No appr-registries dependencies'),
    ({
         'appr': [{
             'name': '%s/titi/rocketchat' % DEFAULT_REGISTRY,
             'version': '0.0.1'
         }]
     }, {
         'dependencies': [{
             'name': 'rocketchat',
             'repository': 'file://%s/titi/rocketchat',
             'version': '0.0.1'
         }],
         'appr': [{
             'name': 'rocketchat',
             'repository': 'file://%s/titi/rocketchat',
             'version': '0.0.1'
         }]
     }),
    ({
         'appr': [{
             'name': '%s/titi/rocketchat' % DEFAULT_REGISTRY,
             'version': '0.0.1',
             'alias': 'rocketchat1'
         }, {
             'name': '%s/titi/rocketchat' % DEFAULT_REGISTRY,
             'version': '0.0.1',
             'alias': 'rocketchat2'
         }]
     }, {
         'dependencies': [{
             'name': 'rocketchat',
             'repository': 'file://%s/titi/rocketchat',
             'version': '0.0.1',
             'alias': 'rocketchat1'
         }, {
             'name': 'rocketchat',
             'repository': 'file://%s/titi/rocketchat',
             'version': '0.0.1',
             'alias': 'rocketchat2'
         }],
         'appr': [{
             'name': 'rocketchat',
             'repository': 'file://%s/titi/rocketchat',
             'version': '0.0.1',
             'alias': 'rocketchat1'
         }, {
             'name': 'rocketchat',
             'repository': 'file://%s/titi/rocketchat',
             'version': '0.0.1',
             'alias': 'rocketchat2'
         }]
     })
])
def test_build_deps_with_empty_values(req, expected, db_with_data1, tmpdir, chhome):
    dest = str(tmpdir.mkdir("charts"))
    hp = Helm()
    if isinstance(expected, dict):
        for dep in expected['dependencies']:
            dep.update({
                'repository': dep['repository'] % dest
            })
        for dep in expected['appr']:
            dep.update({
                'repository': dep['repository'] % dest
            })
    print(expected)
    with requests_mock.mock() as m:
        for dep in req.get('appr', []):
            package = '/'.join(dep['name'].split("/")[-2:])
            response = pull(package, dep['version'], "helm", db_with_data1.Package,
                            db_with_data1.Blob)
            m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/%s/%s/helm/pull" %
                  (package, dep['version']), content=json.dumps(response))
        with open("requirements.yaml", 'wb') as f:
            f.write(yaml.dump(req))
        output = yaml.safe_load(hp.build_dep(dest))

        print(output)
        assert output == expected


def test_build_deps_no_requirements(tmpdir, chhome):
    dest = str(tmpdir.mkdir("charts"))
    hp = Helm()
    assert hp.build_dep(dest) == "No requirements.yaml found"
