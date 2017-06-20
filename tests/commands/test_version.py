import pytest
import requests
import requests_mock
import appr
from appr.client import ApprClient, DEFAULT_REGISTRY, DEFAULT_PREFIX
from appr.commands.version import VersionCmd


def get_versioncmd(cli_parser, args=[]):
    options = cli_parser.parse_args(["version", DEFAULT_REGISTRY] + args)
    return VersionCmd(options)


def test_version_registry_host(cli_parser):
    versioncmd = get_versioncmd(cli_parser)
    assert versioncmd.registry_host == DEFAULT_REGISTRY


def test_version_init(cli_parser):
    versioncmd = get_versioncmd(cli_parser)
    assert versioncmd.api_version is None
    assert versioncmd.registry_host == "http://localhost:5000"
    assert VersionCmd.name == "version"


def test_get_version(cli_parser, capsys):
    versioncmd = get_versioncmd(cli_parser)
    response = '{"appr-server": "0.23.0"}'
    with requests_mock.mock() as m:
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/version",
              complete_qs=True,
              text=response)
        versioncmd.exec_cmd()
        out, err = capsys.readouterr()
        assert out == "Api-version: {u'appr-server': u'0.23.0'}\nClient-version: %s\n""" % appr.__version__
        assert versioncmd._render_dict() == {'api-version': {u'appr-server': u'0.23.0'}, 'client-version': appr.__version__}
        assert versioncmd.api_version == {u'appr-server': u'0.23.0'}


def test_get_version_api_error(cli_parser, capsys):
    versioncmd = get_versioncmd(cli_parser)
    response = '{"appr-server": "0.23.0"}'
    with requests_mock.mock() as m:
        m.get(DEFAULT_REGISTRY + DEFAULT_PREFIX + "/version",
              complete_qs=True,
              text=response, status_code=500)
        versioncmd.exec_cmd()
        out, err = capsys.readouterr()
        assert out == "Api-version: .. Connection error\nClient-version: %s\n""" % appr.__version__
        assert versioncmd._render_dict() == {'api-version': ".. Connection error", 'client-version': appr.__version__}
