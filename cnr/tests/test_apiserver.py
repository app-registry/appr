import os
import urllib
import json
import requests
from flask import request
import pytest
import cnr


@pytest.mark.api
@pytest.mark.integration
class TestServer:
    from cnr.models.kv.filesystem.db import CnrDB
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
        version = "1.0.1"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s/pull" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 200

    def test_pull_package_no_version(self, db_with_data1, client):
        package = "titi/rocketchat"
        version = "1.0.3"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s/pull" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 404

    def test_pull_package_bad_version(self, db_with_data1, client):
        package = "titi/rocketchat"
        version = "abc"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s/pull" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 422

    def test_pull_package_json(self, db_with_data1, client):
        package = "titi/rocketchat"
        version = "1.0.1"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s/pull" % (package, version, media_type))
        res = self.Client(client).get(url, params={'format': 'json'})
        assert res.status_code == 200
        p = db_with_data1.Package.get(package, '1.0.1', 'kpm')
        blob = db_with_data1.Blob.get(p.package, p.digest)
        assert self.json(res)['blob'] == blob.b64blob

    def test_push_package(self, newdb, package_b64blob, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s" % package)
        res = self.Client(client).post(url, body={'version': '2.4.1',
                                                  'media_type': 'kpm',
                                                  'blob': package_b64blob})
        assert res.status_code == 200
        p = newdb.Package.get(package, '2.4.1', 'kpm')
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

    def test_get_blob(self, db_with_data1, client):
        package = "titi/rocketchat"
        p = db_with_data1.Package.get(package)
        blob = db_with_data1.Blob.get(package, p.digest)
        url = self._url_for("api/v1/packages/%s/blobs/sha256/%s" % (package, p.digest))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert self.content(res) == blob.blob

    def test_get_absent_blob(self, newdb, client):
        package = "a/b"
        digest = "12345"
        url = self._url_for("api/v1/packages/%s/blobs/sha256/%s" % (package, digest))
        res = self.Client(client).get(url)
        assert res.status_code == 404

    def test_list_packages(self, db_with_data1, client):
        url = self._url_for("api/v1/packages/")
        res = self.Client(client).get(url)
        assert sorted(self.json(res)) == sorted(db_with_data1.Package.all())

    def test_list_packages_filter_namespace(self, db_with_data1, client):
        url = self._url_for("api/v1/packages/?namespace=ant31")
        res = self.Client(client).get(url)
        assert sorted(self.json(res)) == sorted(db_with_data1.Package.all('ant31'))
        url = self._url_for("api/v1/packages/?namespace=titi")
        res = self.Client(client).get(url)
        assert sorted(self.json(res)) == sorted(db_with_data1.Package.all('titi'))

    def test_list_empty(self, newdb, client):
        url = self._url_for("api/v1/packages")
        res = self.Client(client).get(url)
        assert self.json(res) == []

    def test_delete_package(self, db_with_data1, client):
        package = "titi/rocketchat"
        version = "1.0.1"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        res = self.Client(client).delete(url)
        assert res.status_code == 200
        res = self.Client(client).get(url)
        assert res.status_code == 404

    def test_delete_absent_package(self, newdb, client):
        package = "titi/rocketchat"
        version = "1.0.1"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s" % (package, version, media_type))
        res = self.Client(client).delete(url)
        assert res.status_code == 404

    def test_show_package(self, db_with_data1, client):
        package = "titi/rocketchat"
        version = "1.0.1"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        p = db_with_data1.Package.get(package, "1.0.1", "kpm")
        assert self.json(res)['content']['digest'] == p.digest

    def test_show_package_releases(self, db_with_data1, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s" % (package))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert len(self.json(res)) == 3

    def test_show_package_manifests(self, db_with_data1, client):
        package = "titi/rocketchat"
        release = "1.0.1"
        url = self._url_for("api/v1/packages/%s/%s" % (package, release))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        p = db_with_data1.Package.get(package, "1.0.1", "kpm")
        assert len(self.json(res)['manifests']) == 1
        assert self.json(res)['manifests'][0]['content']['digest'] == p.digest

    def test_show_package_absent(self, newdb, client):
        package = "titi/rocketchat"
        version = "1.0.1"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 404

    def test_show_package_bad_version(self, db_with_data1, client):
        package = "titi/rocketchat"
        version = "abc"
        media_type = "kpm"
        url = self._url_for("api/v1/packages/%s/%s/%s" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 422

    def test_show_package_media_type(self, db_with_data1, client):
        package = "titi/rocketchat"
        package = "titi/rocketchat"
        version = "0.0.1"
        media_type = "helm"
        url = self._url_for("api/v1/packages/%s/%s/%s" % (package, version, media_type))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        p = db_with_data1.Package.get(package, "0.0.1", "helm")
        assert self.json(res)['content']['digest'] == p.digest

    def test_show_channel(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'stable'
        url = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert self.json(res) == db_with_data1.Channel(channel, package).to_dict()

    def test_show_channel_absent_package(self, newdb, client):
        package = "titi/rocketchat"
        channel = 'no'
        url = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(url)
        assert res.status_code == 404

    @pytest.mark.xfail
    def test_show_channel_absent(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'no'
        url = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(url)
        assert res.status_code == 404

    def test_list_channels(self, db_with_data1, client):
        package = "titi/rocketchat"
        url = self._url_for("api/v1/packages/%s/channels" % (package))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert sorted(self.json(res)) == sorted([c.to_dict() for c in db_with_data1.Channel.all(package)])

    def test_list_channels_404(self, newdb, client):
        package = "titi/no"
        url = self._url_for("api/v1/packages/%s/channels" % (package))
        res = self.Client(client).get(url)
        assert res.status_code == 404

    def test_add_channel_release(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'default'
        version = '1.0.1'
        url = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert self.json(res)['releases'] == []
        url = self._url_for("api/v1/packages/%s/channels/%s/%s" % (package, channel, version))
        res = self.Client(client).post(url)
        assert res.status_code == 200
        assert self.json(res)['releases'] == [version]

    def test_add_channel_release_new_chan(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'newchan'
        version = '1.0.1'
        chanurl = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(chanurl)
        # assert res.status_code == 404  # @TODO uncomment
        url = self._url_for("api/v1/packages/%s/channels/%s/%s" % (package, channel, version))
        res = self.Client(client).post(url)
        assert res.status_code == 200
        chanurl = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(chanurl)
        assert res.status_code == 200
        assert self.json(res)['releases'] == [version]

    def test_add_channel_release_absent_release(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'default'
        version = '1.0.2'
        url = self._url_for("api/v1/packages/%s/channels/%s/%s" % (package, channel, version))
        res = self.Client(client).post(url)
        assert res.status_code == 404

    def test_delete_channel_release(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'stable'
        version = '1.0.1'
        url = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert version in self.json(res)['releases']
        url = self._url_for("api/v1/packages/%s/channels/%s/%s" % (package, channel, version))
        res = self.Client(client).delete(url)
        assert res.status_code == 200
        assert version not in self.json(res)['releases']

    def test_delete_channel_release_absent_release(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'stable'
        version = '1.0.2'
        url = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(url)
        assert res.status_code == 200
        assert version not in self.json(res)['releases']
        url = self._url_for("api/v1/packages/%s/channels/%s/%s" % (package, channel, version))
        res = self.Client(client).delete(url)
        assert res.status_code == 404

    def test_create_channel(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'newchan'
        chanurl = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).get(chanurl)
        # assert res.status_code == 404  # @TODO uncomment
        res = self.Client(client).post(chanurl)
        assert res.status_code == 200
        assert self.json(res)['releases'] == []

    def test_create_channel_absent_package(self, newdb, client):
        package = "titi/rocketchat"
        channel = 'newchan'
        chanurl = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).post(chanurl)
        assert res.status_code == 404

    def test_delete_channel(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'stable'
        p = db_with_data1.Package.get(package, "1.0.1", "kpm")
        assert channel in p.channels()
        chanurl = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).delete(chanurl)
        assert res.status_code == 200
        p = db_with_data1.Package.get(package, "1.0.1", "kpm")
        assert channel not in p.channels()

    def test_delete_absent_channel(self, db_with_data1, client):
        package = "titi/rocketchat"
        channel = 'no'
        chanurl = self._url_for("api/v1/packages/%s/channels/%s" % (package, channel))
        res = self.Client(client).delete(chanurl)
        assert res.status_code == 404


BaseTestServer = TestServer


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
