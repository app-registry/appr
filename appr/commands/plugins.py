from __future__ import absolute_import, division, print_function

import os
from os.path import expanduser
import tarfile

import requests

from appr.commands.command_base import CommandBase
from appr.utils import mkdir_p, get_current_script_path

LOCAL_DIR = os.path.dirname(__file__)


def install_helm_plugin(plugin, plugin_info):
    version = plugin['name']
    tarball_src = ("https://github.com/%s/releases/download/%s/registry-helm-plugin.tar.gz" %
                   (plugin_info['repo'], version))
    helm_home = os.getenv("HELM_HOME", os.path.join(expanduser("~"), ".helm"))
    plugin_path = os.getenv("HELM_PLUGIN_DIR", os.path.join(helm_home, "plugins"))
    mkdir_p(plugin_path)
    tardest = os.path.join(plugin_path, "appr-helm-plugin-%s.tar.gz" % version)
    res = requests.get(tarball_src)
    res.raise_for_status()
    with open(tardest, "wb") as f:
        f.write(res.content)
    tar = tarfile.open(tardest, 'r:gz')
    tar.extractall(plugin_path)
    bin_path = os.path.join(plugin_path, "registry/appr")
    if os.path.exists(bin_path):
        os.remove(bin_path)
    execscript = get_current_script_path()
    os.symlink(get_current_script_path(), bin_path)
    return {
        'plugin-version': version,
        'status': 'installed',
        'path': os.path.join(plugin_path, 'registry'),
        'symlink': execscript}


class PluginsCmd(CommandBase):
    name = 'plugins'
    help_message = "Install plugins"
    plugins = {
        'helm': {
            'repo': 'app-registry/appr-helm-plugin',
            'install_method': install_helm_plugin}}
    output_default = "yaml"

    def __init__(self, options):
        super(PluginsCmd, self).__init__(options)
        self.plugin = options.plugin
        self.status = ""

    @classmethod
    def get_latest_plugin(cls, plugin_name):
        path = "https://api.github.com/repos/%s/tags" % cls.plugins[plugin_name]['repo']
        resp = requests.get(path)
        resp.raise_for_status()
        json_resp = resp.json()
        return json_resp[0]

    @classmethod
    def _init_args(cls, subcmd):
        subcmd.add_argument("plugin", choices=['helm'], help='plugin')

    @classmethod
    def _install(cls, options, unknown=None):
        plugin_name = options.plugin
        plugin = cls.get_latest_plugin(plugin_name)
        cmd = cls(options)
        cmd.status = cls.plugins[plugin_name]['install_method'](plugin, cls.plugins[plugin_name])
        cmd.render()

    @classmethod
    def _add_arguments(cls, parser):
        sub = parser.add_subparsers()
        install_cmd = sub.add_parser('install')
        cls._init_args(install_cmd)
        install_cmd.set_defaults(func=cls._install)

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self.status
