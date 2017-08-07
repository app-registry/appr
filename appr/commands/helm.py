from __future__ import absolute_import, division, print_function

import argparse
import os
import tempfile

from appr.commands.command_base import CommandBase
from appr.commands.pull import PullCmd
from appr.plugins.helm import Helm

LOCAL_DIR = os.path.dirname(__file__)


class HelmCmd(CommandBase):
    name = 'helm'
    help_message = 'Deploy with Helm on Kubernetes'
    parse_unknown = True

    def __init__(self, options):
        super(HelmCmd, self).__init__(options)
        self.status = {}

    def exec_helm_cmd(self, cmd, options, helm_opts):
        pull_cmd = PullCmd(options)
        pull_cmd.exec_cmd(render=False)
        helm_cli = Helm()
        output = helm_cli.action(cmd, pull_cmd.path, helm_opts)
        self.status = {'result': output}
        self.render()

    @classmethod
    def _install(cls, options, unknown=None):
        cmd = cls(options)
        cmd.exec_helm_cmd('install', options, unknown)

    @classmethod
    def _upgrade(cls, options, unknown=None):
        cmd = cls(options)
        cmd.exec_helm_cmd('upgrade', options, unknown)

    @classmethod
    def _dep_pull(cls, options, unknown=None):
        cmd = cls(options)
        helm_cli = Helm()
        cmd.status = {'result': helm_cli.build_dep(dest=options.dest, overwrite=options.overwrite)}
        cmd.render()

    @classmethod
    def _init_args(cls, subcmd):
        cls._add_registryhost_option(subcmd)
        cls._add_packagename_option(subcmd)
        cls._add_packageversion_option(subcmd)
        subcmd.add_argument('-t', '--media-type', default='helm', help=argparse.SUPPRESS)

        subcmd.add_argument('--dest', default=tempfile.gettempdir(),
                            help='directory used to extract resources')
        subcmd.add_argument('--tarball', action='store_true', default=True, help=argparse.SUPPRESS)

    @classmethod
    def _init_dep_args(cls, subcmd):
        subcmd.add_argument('--dest', default="appr_charts",
                            help='directory used to extract resources')
        subcmd.add_argument('--overwrite', action='store_true', default=False,
                            help="auto-merge requirements.yaml with the appr dependencies")

    @classmethod
    def _add_arguments(cls, parser):
        sub = parser.add_subparsers()
        install_cmd = sub.add_parser('install')
        upgrade_cmd = sub.add_parser('upgrade')
        dep_pull_cmd = sub.add_parser('dep')
        cls._init_dep_args(dep_pull_cmd)
        cls._init_args(install_cmd)
        cls._init_args(upgrade_cmd)
        install_cmd.set_defaults(func=cls._install)
        upgrade_cmd.set_defaults(func=cls._upgrade)
        dep_pull_cmd.set_defaults(func=cls._dep_pull)

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self.status['result']
