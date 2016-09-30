import json
import logging
from urlparse import urlparse, urljoin
import requests
import cnrclient
from cnrclient.auth import CnrAuth
from cnrclient.discovery import ishosted, discover_sources


logger = logging.getLogger(__name__)
DEFAULT_REGISTRY = 'http://localhost:5000'
DEFAULT_PREFIX = "/cnr"


class CnrClient(object):
    def __init__(self, endpoint=DEFAULT_REGISTRY, api_prefix=DEFAULT_PREFIX):
        self.api_prefix = api_prefix
        if endpoint is None:
            endpoint = DEFAULT_REGISTRY
        self.endpoint = urlparse(endpoint)
        self.auth = CnrAuth()
        self._headers = {'Content-Type': 'application/json',
                         'User-Agent': "cnrpy-cli: %s" % cnrclient.__version__}

    def _url(self, path):
        return urljoin(self.endpoint.geturl(), self.endpoint.path + self.api_prefix + path)

    @property
    def headers(self):
        token = self.auth.token
        headers = {}
        headers.update(self._headers)
        if token is not None:
            headers['Authorization'] = token
        return headers

    def version(self):
        path = "/version"
        resp = requests.get(self._url(path), headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def pull(self, name, version=None):
        if ishosted(name):
            sources = discover_sources(name)
            path = sources[0]
        else:
            organization, name = name.split("/")
            path = self._url("/api/v1/packages/%s/%s/pull" % (organization, name))
        params = {"version": version}
        resp = requests.get(path, params=params, headers=self.headers)
        resp.raise_for_status()
        return resp.content

    def list_packages(self, user=None, organization=None):
        path = "/api/v1/packages"
        params = {}
        if user:
            params['username'] = user
        if organization:
            params["organization"] = organization
        resp = requests.get(self._url(path), params=params, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def push(self, name, body, force=False):
        organization, pname = name.split("/")
        body['name'] = pname
        body['organization'] = organization
        body['package'] = name
        path = "/api/v1/packages/%s/%s" % (organization, pname)
        resp = requests.post(self._url(path),
                             params={"force": str(force).lower()},
                             data=json.dumps(body), headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def login(self, username, password):
        path = "/api/v1/users/login"
        self.auth.delete_token()
        resp = requests.post(self._url(path),
                             data=json.dumps({"user": {"username": username, "password": password}}),
                             headers=self.headers)
        resp.raise_for_status()
        result = resp.json()
        self.auth.token = result['token']
        return result

    def signup(self, username, password, password_confirmation, email):
        path = "/api/v1/users"
        self.auth.delete_token()
        resp = requests.post(self._url(path),
                             data=json.dumps({"user": {"username": username,
                                                       "password": password,
                                                       "password_confirmation": password_confirmation,
                                                       "email": email}}),
                             headers=self.headers)
        resp.raise_for_status()
        result = resp.json()
        self.auth.token = result['token']
        return result

    def delete_package(self, name, version=None):
        organization, name = name.split("/")
        path = "/api/v1/packages/%s/%s" % (organization, name)
        params = {}
        if version:
            params['version'] = version
        resp = requests.delete(self._url(path), params=params, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def _crud_channel(self, name, channel='', action='get'):
        if channel is None:
            channel = ''
        path = "/api/v1/packages/%s/channels/%s" % (name, channel)
        resp = getattr(requests, action)(self._url(path), params={}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def show_channels(self, name, channel=None):
        return self._crud_channel(name, channel)

    def create_channel(self, name, channel):
        return self._crud_channel(name, channel, 'post')

    def delete_channel(self, name, channel):
        return self._crud_channel(name, channel, 'delete')

    def create_channel_release(self, name, channel, release):
        path = "%s/%s" % (channel, release)
        return self._crud_channel(name, path, 'post')

    def delete_channel_release(self, name, channel, release):
        path = "%s/%s" % (channel, release)
        return self._crud_channel(name, path, 'delete')
