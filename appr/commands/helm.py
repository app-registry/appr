from __future__ import absolute_import, division, print_function

import argparse
import os
import tempfile
from copy import copy
from appr.commands.command_base import CommandBase
from appr.commands.pull import PullCmd
from appr.plugins.helm import Helm

LOCAL_DIR = os.path.dirname(__file__)


def helm_description(cmd, examples):
    return """
Fetch a Chart from the app-registry and execute `helm {cmd}`.
Helm's options can be passed on the command:
$ appr helm {cmd} [APPR_OPTS] -- [HELM_OPTS]
{examples}

""".format(cmd=cmd, examples=examples)


class HelmCmd(CommandBase):
    name = 'helm'
    help_message = 'Deploy with Helm on Kubernetes'
    parse_unknown = True
    plugin_subcommands = ['dep', 'install', 'upgrade']

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
        from appr.commands.cli import get_parser, all_commands
        sub = parser.add_subparsers()
        install_cmd = sub.add_parser(
            'install', help="Fetch the Chart and execute `helm install`",
            formatter_class=argparse.RawDescriptionHelpFormatter, description=helm_description(
                "install",
                "$ appr helm install quay.io/ant31/cookieapp -- --set imageTag=v0.4.5 --namespace demo"
            ), epilog="\nhelm options:\n  See 'helm install --help'")
        upgrade_cmd = sub.add_parser(
            'upgrade', help="Fetch the Chart and execute `helm upgrade`",
            formatter_class=argparse.RawDescriptionHelpFormatter, description=helm_description(
                "upgrade",
                "$ appr helm upgrade quay.io/ant31/cookieapp -- release-name --set foo=bar --set foo=newbar"
            ), epilog="\nhelm options:\n  See 'helm upgrade --help'")
        dep_pull_cmd = sub.add_parser(
            'dep', help="Download Charts from the requirements.yaml using app-registry")
        cls._init_dep_args(dep_pull_cmd)
        cls._init_args(install_cmd)
        cls._init_args(upgrade_cmd)
        install_cmd.set_defaults(func=cls._install)
        upgrade_cmd.set_defaults(func=cls._upgrade)
        dep_pull_cmd.set_defaults(func=cls._dep_pull)
        other_cmds = copy(all_commands())
        other_cmds.pop("helm")
        get_parser(other_cmds, parser, sub, {'APPR_DEFAULT_MEDIA_TYPE': 'helm'})

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self.status['result']
