from __future__ import absolute_import, division, print_function

import argparse
import os

from appr.commands.channel import ChannelCmd
from appr.commands.config import ConfigCmd
from appr.commands.delete_package import DeletePackageCmd
from appr.commands.helm import HelmCmd
from appr.commands.inspect import InspectCmd
from appr.commands.list_package import ListPackageCmd
from appr.commands.login import LoginCmd
from appr.commands.logout import LogoutCmd
from appr.commands.plugins import PluginsCmd
from appr.commands.pull import PullCmd
from appr.commands.push import PushCmd
from appr.commands.jsonnet import JsonnetCmd
from appr.commands.runserver import RunServerCmd
from appr.commands.show import ShowCmd
from appr.commands.version import VersionCmd
from appr.commands.deploy import DeployCmd


def all_commands():
    return {
        InspectCmd.name: InspectCmd,
        PushCmd.name: PushCmd,
        VersionCmd.name: VersionCmd,
        PullCmd.name: PullCmd,
        ShowCmd.name: ShowCmd,
        LoginCmd.name: LoginCmd,
        LogoutCmd.name: LogoutCmd,
        ChannelCmd.name: ChannelCmd,
        DeletePackageCmd.name: DeletePackageCmd,
        PluginsCmd.name: PluginsCmd,
        ConfigCmd.name: ConfigCmd,
        DeployCmd.name: DeployCmd,
        ListPackageCmd.name: ListPackageCmd,
        HelmCmd.name: HelmCmd,
        RunServerCmd.name: RunServerCmd,
        JsonnetCmd.name: JsonnetCmd, }


def get_parser(commands):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command help')
    for command_class in commands.values():
        command_class.add_parser(subparsers)
    return parser


def cli():
    try:
        parser = get_parser(all_commands())
        unknown = None
        args, unknown = parser.parse_known_args()
        if args.parse_unknown:
            args.func(args, unknown)
        else:
            args = parser.parse_args()
            args.func(args)

    except (argparse.ArgumentTypeError, argparse.ArgumentError) as exc:
        if os.getenv("APPR_DEBUG", "false") == "true":
            raise
        else:
            parser.error(exc.message)
