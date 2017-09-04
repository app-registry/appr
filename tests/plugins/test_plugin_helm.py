from __future__ import absolute_import, division, print_function

import json
import pytest
import requests_mock
from appr.plugins.helm import Helm
from appr.client import DEFAULT_PREFIX, DEFAULT_REGISTRY
from appr.api.impl.registry import pull


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
        assert deps == {
            'rocketchat': {
                "repository": "file://%s/titi/rocketchat" % (tempdir, ),
                "version": version,
                "name": 'rocketchat',
                "randomKey": 'oky'
            },
        }
