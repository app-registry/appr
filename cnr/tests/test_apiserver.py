import os
import urllib
import json
import requests
from flask import request
import pytest
import cnr


@pytest.mark.api
@pytest.mark.integration
class BaseTestServer(object):
    from cnr.models.db_base import CnrDB
    DB_CLASS = CnrDB

    @pytest.fixture()
    def db(self):
        return self.DB_CLASS

    class Client(object):
        def __init__(self, client):
            self.client = client

        def _request(self, method, path, params, body):
            if params:
                path = path + "?" + urllib.urlencode(params)
            return getattr(self.client, method)(path, data=body)

        def get(self, path, params=None, body=None):
            return self._request('get', path, params, body)

        def delete(self, path, params=None, body=None):
            return self._request('delete', path, params, body)

        def post(self, path, params=None, body=None):
            return self._request('post', path, params, body)

    def json(self, res):
        return res.json

    def content(self, res):
        return res.data

    def _url_for(self, path):
        return "/" + self.api_prefix + path

    @property
    def api_prefix(self):
        return os.getenv("CNR_API_PREFIX", "")

    def test_version(self, client):
        url = self._url_for("version")
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert self.json(res) == {"cnr-api": cnr.__version__}

    def test_search_package_match(self, db_with_data1, client):
        url = self._url_for("api/v1/packages/search")
        res = self.Client(client).get(url, params={'q': 'titi'})
        assert res.status_code == 200
        assert self.json(res) == ['titi/rocketchat']

    def test_search_package_no_match(self, db_with_data1, client):
        url = self._url_for("api/v1/packages/search")
        res = self.Client(client).get(url, params={'q': 'toto'})
        assert res.status_code == 200
        assert self.json(res) == []

    # @TODO check content
    def test_pull_package(self, db_with_data1, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s/pull" % package)
        res = self.Client(client).get(url, params={'version': '1.0.1', 'media_type': 'kpm'})
        assert res.status_code == 200

    def test_pull_package_no_version(self, db_with_data1, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s/pull" % package)
        res = self.Client(client).get(url, params={'version': '1.0.3', 'media_type': 'kpm'})
        assert res.status_code == 404

    def test_pull_package_bad_version(self, db_with_data1, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s/pull" % package)
        res = self.Client(client).get(url, params={'version': 'bac', 'media_type': 'kpm'})
        assert res.status_code == 422

    def test_pull_package_json(self, db_with_data1, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s/pull" % package)
        res = self.Client(client).get(url, params={'version': '1.0.1', 'media_type': 'kpm', 'format': 'json'})
        assert res.status_code == 200
        p = db_with_data1.Package.get('titi/rocketchat', '1.0.1', 'kpm')
        blob = db_with_data1.Blob.get(p.package, p.digest)
        assert self.json(res)['blob'] == blob.b64blob

    def test_push_package(self, newdb, package_b64blob, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s" % package)
        res = self.Client(client).post(url, body={'version': '2.4.1',
                                                  'media_type': 'kpm',
                                                  'blob': package_b64blob})
        assert res.status_code == 200
        p = newdb.Package.get('titi/rocketchat', '2.4.1', 'kpm')
        blob = newdb.Blob.get(p.package, p.digest)
        assert blob.b64blob == package_b64blob

    def test_push_package_bad_version(self, newdb, package_b64blob, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s" % package)
        res = self.Client(client).post(url, body={'package': package,
                                                  'version': 'anc',
                                                  'media_type': 'kpm',
                                                  'blob': package_b64blob})
        assert res.status_code == 422

    def test_push_package_already_exists(self, db_with_data1, package_b64blob, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s" % package)
        res = self.Client(client).post(url, body={'package': package,
                                                  'version': '1.0.1',
                                                  'media_type': 'kpm',
                                                  'blob': package_b64blob})
        assert res.status_code == 409

    def test_push_package_already_exists_force(self, db_with_data1, package_b64blob, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s" % package)
        res = self.Client(client).post(url, body={'package': package,
                                                  'version': '1.0.1',
                                                  'force': 'true',
                                                  'media_type': 'kpm',
                                                  'blob': package_b64blob})
        assert res.status_code == 200


@pytest.mark.usefixtures('live_server')
class LiveTestServer(BaseTestServer):
    class Client(object):
        def __init__(self, client):
            self.client = requests

        def _request(self, method, path, params, body):
            return getattr(self.client, method)(path, params=params, data=json.dumps(body))

        def get(self, path, params=None, body=None):
            return self._request('get', path, params, body)

        def delete(self, path, params=None, body=None):
            return self._request('delete', path, params, body)

        def post(self, path, params=None, body=None):
            return self._request('post', path, params, body)

    def content(self, res):
        return res.content

    def _url_for(self, path):
        return request.url_root + self.api_prefix + path

    @pytest.fixture(autouse=True)
    def client(self, client):
        return requests

    def json(self, res):
        return res.json()


def get_server_class():
    if os.getenv("CNR_TEST_LIVESERVER", "false") == 'true':
        return LiveTestServer
    else:
        return BaseTestServer


ServerTest = get_server_class()
