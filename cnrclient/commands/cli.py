import argparse
import os

from cnrclient.commands.push import PushCmd
from cnrclient.commands.inspect import InspectCmd
from cnrclient.commands.pull import PullCmd
from cnrclient.commands.version import VersionCmd
from cnrclient.commands.show import ShowCmd
from cnrclient.commands.login import LoginCmd
from cnrclient.commands.logout import LogoutCmd
from cnrclient.commands.channel import ChannelCmd
from cnrclient.commands.list_package import ListPackageCmd
from cnrclient.commands.delete_package import DeletePackageCmd
from cnrclient.commands.plugins import PluginsCmd
from cnrclient.commands.config import ConfigCmd


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
        ListPackageCmd.name: ListPackageCmd,
    }


def get_parser(commands):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command help')
    for command_class in commands.values():
        command_class.add_parser(subparsers)
    return parser


def cli():
    try:
        parser = get_parser(all_commands())
        args = parser.parse_args()
        args.func(args)
    except (argparse.ArgumentTypeError, argparse.ArgumentError) as exc:
        if os.getenv("CNR_DEBUG", "false") == "true":
            raise
        else:
            parser.error(exc.message)
