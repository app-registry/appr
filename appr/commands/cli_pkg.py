from __future__ import absolute_import, division, print_function

import argparse
import os

from appr.commands.package.generate import GenerateCmd
from appr.commands.package.extract import ExtractCmd
from appr.commands.package.version import VersionCmd
from appr.commands.package.inspect import InspectCmd


def all_commands():
    return {
        VersionCmd.name: VersionCmd,
        ExtractCmd.name: ExtractCmd,
        InspectCmd.name: InspectCmd,
        GenerateCmd.name: GenerateCmd,
    }


def get_parser(commands, parser=None, subparsers=None, env=None):
    if parser is None:
        parser = argparse.ArgumentParser()

    if subparsers is None:
        subparsers = parser.add_subparsers(help='command help')

    for cls in commands.values():
        subparser = subparsers.add_parser(cls.name, help=cls.help_message)
        cls._add_arguments(subparser)
        subparser.set_defaults(func=cls.call, env=env, which_cmd=cls.name,
                               parse_unknown=cls.parse_unknown)
    return parser


def set_cmd_env(env):
    """ Allow commands to Set environment variables after being called """
    if env is not None:
        for key, value in env.items():
            os.environ[key] = value


def cli():
    try:
        parser = get_parser(all_commands())
        unknown = None
        args, unknown = parser.parse_known_args()
        set_cmd_env(args.env)
        if args.parse_unknown:
            args.func(args, unknown)
        else:
            args = parser.parse_args()
            args.func(args)

    except (argparse.ArgumentTypeError, argparse.ArgumentError) as exc:
        if os.getenv("KUBECTL_PACKAGE_DEBUG", "false") == "true":
            raise
        else:
            parser.error(exc)
