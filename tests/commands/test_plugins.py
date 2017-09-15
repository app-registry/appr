from __future__ import absolute_import, division, print_function

import platform
import os
import json
import pytest
import requests_mock

from appr import SYSTEM
from appr.commands.plugins import PluginsCmd
from appr.utils import convert_utf8


def parse_args(cli_parser, args):
    return cli_parser.parse_args(["plugins"] + args)


def get_pluginscmd(cli_parser, args=[]):
    options = parse_args(cli_parser, args)
    return PluginsCmd(options)


def test_plugins_init(cli_parser, fake_home):
    pluginscmd = get_pluginscmd(cli_parser, ["install", "helm"])
    assert pluginscmd.plugin == "helm"
    assert PluginsCmd.name == "plugins"


def test_get_latest_tag(cli_parser, fake_home, monkeypatch, plugin_helm_releases):
    with requests_mock.mock() as m:
        m.get("https://api.github.com/repos/app-registry/appr-helm-plugin/tags",
              text=plugin_helm_releases)
        assert PluginsCmd.get_latest_plugin('helm') == json.loads(plugin_helm_releases)[0]
        assert PluginsCmd.get_latest_plugin('helm')['name'] == 'v0.5.1'


@pytest.mark.skipif(SYSTEM == "windows", reason="Plugin install not supported on windows")
@pytest.mark.parametrize("helm_home,plugin_home,path", [
    (None, None, ".helm/plugins"),
    ("helm-home", None, "helm-home/plugins"),
    ("helm-home", "helm-plugins", "helm-plugins"),
    (None, "helm-plugins2", "helm-plugins2"),
])
def test_install_helm_plugin(helm_home, plugin_home, path, capsys, cli_parser, fake_home,
                             monkeypatch, plugin_helm_tarball, plugin_helm_releases):
    homepath = os.getenv('HOME')
    registry_plugin = os.path.join(homepath, path, "registry")
    if helm_home:
        monkeypatch.setenv("HELM_HOME", os.path.join(homepath, helm_home))

    if plugin_home:
        monkeypatch.setenv("HELM_PLUGIN_DIR", os.path.join(homepath, plugin_home))

    with requests_mock.mock() as m:
        tarname = "helm-registry_%s.tar.gz" % platform.system().lower()
        m.get("https://api.github.com/repos/app-registry/appr-helm-plugin/tags",
              text=plugin_helm_releases)
        m.get("https://github.com/app-registry/appr-helm-plugin/releases/download/v0.5.1/%s" %
              tarname, content=plugin_helm_tarball)
        args = parse_args(cli_parser, ["--output", "json", "install", "helm"])
        args.func(args)
        out, err = capsys.readouterr()

        homepath = os.getenv('HOME')
        for fname in ['plugin.yaml', 'appr', 'cnr.sh']:
            assert os.path.exists(os.path.join(homepath, registry_plugin, fname))
        output = json.loads(out)
        output.pop('symlink')
        assert convert_utf8(output) == {
            'path':
                os.path.join(homepath, registry_plugin),
            'plugin-version':
                'v0.5.1',
            'platform':
                platform.system().lower(),
            'source':
                'https://github.com/app-registry/appr-helm-plugin/releases/download/v0.5.1/%s' %
                tarname,
            'status':
                'installed'
        }
