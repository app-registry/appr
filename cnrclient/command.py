#!/usr/bin/env python
import argparse

from cnrclient.utils import parse_package_name
from cnrclient.commands import all_commands


class PackageName(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        try:
            name = value[0]
            package_parts = parse_package_name(name)
            if package_parts['host'] is not None:
                setattr(namespace, "registry_host", package_parts['host'])
            if package_parts['version'] is not None:
                setattr(namespace, 'version', package_parts['version'])
            package = package_parts['package']
        except ValueError as exc:
            raise parser.error(exc.message)
        setattr(namespace, self.dest, package)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command help')
    for _, command_class in all_commands.iteritems():
        command_class.add_parser(subparsers)
    return parser


def cli():
    try:
        parser = get_parser()
        args = parser.parse_args()
        args.func(args)
    except (argparse.ArgumentTypeError, argparse.ArgumentError) as e:
        parser.error(e.message)
