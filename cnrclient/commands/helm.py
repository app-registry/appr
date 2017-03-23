import os
import argparse

from cnrclient.commands.command_base import CommandBase
from cnrclient.commands.pull import PullCmd
from cnrclient.plugins.helm import Helm

LOCAL_DIR = os.path.dirname(__file__)


class HelmCmd(CommandBase):
    name = 'helm'
    help_message = "Deploy with Helm on Kubernetes"
    parse_unknown = True

    def __init__(self, options):
        super(HelmCmd, self).__init__(options)
        self.status = {}

    def _exec_cmd(self, cmd, options, helm_opts):
        pull_cmd = PullCmd(options)
        pull_cmd._call()
        helm_cli = Helm()
        output = helm_cli.action(cmd, pull_cmd.path, helm_opts)
        self.status = {"result": output}
        self.render()

    @classmethod
    def _install(cls, options, unknown=None):
        cmd = cls(options)
        cmd._exec_cmd("install", options, unknown)

    @classmethod
    def _upgrade(cls, options, unknown=None):
        cmd = cls(options)
        cmd._exec_cmd("upgrade", options, unknown)

    @classmethod
    def _init_args(cls, subcmd):
        cls._add_registryhost_option(subcmd)
        cls._add_packagename_option(subcmd)
        cls._add_packageversion_option(subcmd)
        subcmd.add_argument("-t", "--media-type", default="helm",
                            help=argparse.SUPPRESS)

        subcmd.add_argument("--dest", default="/tmp",
                            help="directory used to extract resources")
        subcmd.add_argument("--tarball", action="store_true", default=True,
                            help=argparse.SUPPRESS)

    @classmethod
    def _add_arguments(cls, parser):
        sub = parser.add_subparsers()
        install_cmd = sub.add_parser('install')
        upgrade_cmd = sub.add_parser('upgrade')
        cls._init_args(install_cmd)
        cls._init_args(upgrade_cmd)
        install_cmd.set_defaults(func=cls._install)
        upgrade_cmd.set_defaults(func=cls._upgrade)

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self.status['result']
