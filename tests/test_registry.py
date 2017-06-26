from base64 import b64encode
import json
import pytest
import requests
import requests_mock
from appr.client import ApprClient, DEFAULT_REGISTRY, DEFAULT_PREFIX
import appr


@pytest.fixture()
def channels_data():
    return {'dev': {'current': '1.0.0-rc', 'name': 'dev'}}


@pytest.fixture(autouse=True)
def fakehome(fake_home):
    pass


def test_headers_without_auth():
    r = ApprClient()
    assert sorted(r.headers.keys()) == ['Content-Type', 'User-Agent']
    assert r.headers["Content-Type"] == "application/json"
    assert r.headers["User-Agent"] == "apprpy-cli/%s" % appr.__version__


def test_headers_with_auth():
    r = ApprClient()
    r.auth.add_token('*', 'titi')
    assert sorted(r.headers.keys()) == ["Authorization", 'Content-Type', 'User-Agent']
    assert r.headers["Authorization"] == "titi"
    assert r.headers["Content-Type"] == "application/json"
    assert r.headers["User-Agent"] == "apprpy-cli/%s" % appr.__version__


def test_default_endpoint():
    r = ApprClient(endpoint=None)
    assert r.endpoint.geturl() == DEFAULT_REGISTRY + DEFAULT_PREFIX


def test_url():
    r = ApprClient(endpoint="http://test.com")
    assert r._url("/test") == "http://test.com" + DEFAULT_PREFIX + "/test"


def test_url_prefix():
    r = ApprClient(endpoint="http://test.com/test")
    assert r._url("/2") == "http://test.com/test" + DEFAULT_PREFIX + "/2"


def test_pull():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = b'package_data'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/orga/p1/1.0.0/helm/pull", content=response)
        assert r.pull("orga/p1", {"value": "1.0.0", "key": "version"}, "helm") == response


def test_pull_channel(channels_data):
    r = ApprClient()
    with requests_mock.mock() as m:
        response = b'package_data'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/orga/p1/1.0.0-rc/helm/pull", content=response)
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/orga/p1/channels/dev",
              text=json.dumps(channels_data['dev']))
        assert r.pull("orga/p1", {"value": "dev", "key": "channel"}, "helm") == response


def test_pull_digest():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = b'package_data'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/orga/p1/blobs/sha256/2432", content=response)
        assert r.pull("orga/p1", {"key": "digest", "value": "2432"}, "helm") == response


def test_pull_version():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = b'package_data'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/orga/p1/0.8.1/helm/pull", content=response)
        assert r.pull("orga/p1", {"key": "version", "value": "0.8.1"}, "helm") == response


def test_pull_discovery_https(discovery_html):
    r = ApprClient()
    with requests_mock.mock() as m:
        response = b'package_data'
        m.get("https://appr.sh/?appr-discovery=1", text=discovery_html, complete_qs=True)
        m.get("https://api.kubespray.io/api/v1/packages/orga/p1/pull", content=response)
        assert r.pull("appr.sh/orga/p1", {"key": "version", "value": "1.0.0"}, "helm") == response


def test_pull_discovery_http(discovery_html):
    r = ApprClient()
    with requests_mock.mock() as m:
        response = b'package_data'
        m.get("https://appr.sh/?appr-discovery=1", text="<html/>", complete_qs=True)
        m.get("http://appr.sh/?appr-discovery=1", text=discovery_html, complete_qs=True)
        m.get("https://api.kubespray.io/api/v1/packages/orga/p1/pull", content=response)
        assert r.pull("appr.sh/orga/p1", {"key": "version", "value": "1.0.0"}, "helm") == response


def test_pull_with_version():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = b'package_data'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/orga/p1/1.0.1/helm/pull", complete_qs=True, content=response)
        assert r.pull("orga/p1", {"key": "version", "value": "1.0.1"}, "helm") == response


def test_list_packages():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages", text=response)
        assert json.dumps(r.list_packages({})) == response


def test_list_packages_username():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages?username=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages({'username': "ant31"})) == response


def test_list_packages_orga():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages?namespace=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages({'namespace': "ant31"})) == response


def test_list_packages_orga_and_user():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages?username=titi&namespace=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages({"username": "titi", "namespace": "ant31"})) == response


def test_delete_package():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/ant31/kube-ui/1.4.3/helm", complete_qs=True, text=response)
        assert r.delete_package("ant31/kube-ui", "1.4.3", "helm") == {"packages": "true"}


def test_delete_package_version():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/ant31/kube-ui/1.4.3/helm", complete_qs=True, text=response)
        assert r.delete_package(name="ant31/kube-ui", version="1.4.3", media_type="helm") == {"packages": "true"}


def test_delete_package_unauthorized():
    r = ApprClient()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/ant31/kube-ui/1.4.3/helm",
                 complete_qs=True,
                 text=response,
                 status_code=401)
        with pytest.raises(requests.HTTPError):
            r.delete_package("ant31/kube-ui", "1.4.3", "helm")


def test_push_unauthorized():
    r = ApprClient()
    with requests_mock.mock() as m:
        body = {"blob": "fdsfds"}
        response = b'{"packages": "true"}'
        m.post(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/ant31/kube-ui?force=false",
               complete_qs=True,
               content=response,
               status_code=401)
        with pytest.raises(requests.HTTPError):
            r.push(name="ant31/kube-ui", body=body)


def test_push():
    body = {"blob": b64encode(b"testdata").decode('utf-8')}
    r = ApprClient()
    response = '{"packages": "true"}'
    with requests_mock.mock() as m:
        m.post(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/ant31/kube-ui?force=false",
               complete_qs=True,
               text=response)
        assert json.dumps(r.push(name="ant31/kube-ui", body=body)) == json.dumps(json.loads(response))


def test_push_force():
    body = {"blob": b64encode(b"foobar").decode('utf-8')}
    r = ApprClient()
    response = '{"packages": "true"}'
    with requests_mock.mock() as m:
        m.post(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/api/v1/packages/ant31/kube-ui?force=true",
               complete_qs=True,
               text=response)
        assert json.dumps(r.push(name="ant31/kube-ui", body=body, force=True)) == json.dumps(json.loads(response))


def test_get_version():
    r = ApprClient()
    response = '{"appr-server": "0.23.0"}'
    with requests_mock.mock() as m:
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/version",
              complete_qs=True,
              text=response)
        assert json.dumps(r.version()) == json.dumps(json.loads(response))
