from __future__ import absolute_import, division, print_function

import argparse
import copy
import json
import os
import re

import requests
import yaml

from appr.client import ApprClient
from appr.utils import parse_package_name, parse_version, split_package_name
from appr.render_jsonnet import RenderJsonnet


def _set_package(parser, namespace, dest, package_parts):
    parsed_version = parse_version(package_parts['version'])
    setattr(namespace, "registry_host", package_parts['host'])
    setattr(namespace, 'version', parsed_version['value'])
    setattr(namespace, 'version_parts', parsed_version)
    package = "%s/%s" % (package_parts['namespace'], package_parts['package'])
    setattr(namespace, dest, package)
    setattr(namespace, "package_parts", package_parts)


class PackageName(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        try:
            name = value[0]
            package_parts = parse_package_name(name)
            _set_package(parser, namespace, self.dest, package_parts)
        except ValueError as exc:
            raise parser.error(str(exc))


class RegistryHost(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, value[0])


class PackageSplit(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        name = value
        package_parts = split_package_name(name)
        _set_package(parser, namespace, self.dest, package_parts)


class LoadVariables(argparse.Action):
    def _parse_cmd(self, var):
        r = {}
        try:
            return json.loads(var)
        except:
            for v in var.split(","):
                sp = re.match("(.+?)=(.+)", v)
                if sp is None:
                    raise ValueError("Malformed variable: %s" % v)
                key, value = sp.group(1), sp.group(2)
                r[key] = value
        return r

    def _load_from_file(self, filename, ext):
        with open(filename, 'r') as f:
            if ext in ['.yml', '.yaml']:
                return yaml.load(f.read())
            elif ext == '.json':
                return json.loads(f.read())
            elif ext in [".jsonnet", "libjsonnet"]:
                r = RenderJsonnet()
                return r.render_jsonnet(f.read())
            else:
                raise ValueError("File extension is not in [yaml, json, jsonnet]: %s" % filename)

    def load_variables(self, var):
        _, ext = os.path.splitext(var)
        if ext not in ['.yaml', '.yml', '.json', '.jsonnet']:
            return self._parse_cmd(var)
        else:
            return self._load_from_file(var, ext)

    def __call__(self, parser, namespace, values, option_string=None):
        items = copy.copy(argparse._ensure_value(namespace, self.dest, {}))
        try:
            items.update(self.load_variables(values))
        except ValueError as exc:
            raise parser.error(option_string + ": " + str(exc))
        setattr(namespace, self.dest, items)


class CommandBase(object):
    name = 'command-base'
    help_message = 'describe the command'
    RegistryClient = ApprClient
    default_media_type = "-"
    parse_unknown = False
    output_default = 'text'

    def __init__(self, args_options, unknown=None):
        self.unknown = unknown
        self.args_options = args_options
        self.output = args_options.output

    def render(self):
        if self.output == 'none':
            return
        elif self.output == 'json':
            self._render_json()
        elif self.output == 'yaml':
            self._render_yaml()
        else:
            print(self._render_console())

    def render_error(self, payload):
        if self.output == 'json':
            self._render_json(payload)
        elif self.output == 'yaml':
            self._render_yaml(payload)
        else:
            raise argparse.ArgumentTypeError("\n" + yaml.safe_dump(
                payload, default_flow_style=False, width=float("inf")))

    @classmethod
    def call(cls, options, unknown=None, render=True):
        # @TODO(ant31): all methods should have the 'unknown' parameter
        if cls.parse_unknown:
            obj = cls(options, unknown)
        else:
            obj = cls(options)
        obj.exec_cmd(render=render)

    def exec_cmd(self, render=True):
        try:
            self._call()
        except requests.exceptions.RequestException as exc:
            payload = {"message": str(exc)}
            if exc.response is not None:
                content = None
                try:
                    content = exc.response.json()
                except ValueError:
                    content = exc.response.content
                payload["response"] = content
            self.render_error(payload)
            exit(2)
        if render:
            self.render()

    @classmethod
    def add_parser(cls, subparsers, env=None):
        parser = subparsers.add_parser(cls.name, help=cls.help_message)
        cls._add_output_option(parser)
        cls._add_arguments(parser)
        parser.set_defaults(func=cls.call, env=env, which_cmd=cls.name,
                            parse_unknown=cls.parse_unknown)

    def _render_json(self, value=None):
        if not value:
            value = self._render_dict()
        print(json.dumps(value, indent=2, separators=(',', ': ')))

    def _render_dict(self):
        raise NotImplementedError

    def _render_console(self):
        raise NotImplementedError

    def _render_yaml(self, value=None):
        if not value:
            value = self._render_dict()
        print(yaml.safe_dump(value, default_flow_style=False, width=float("inf")))

    def _call(self):
        raise NotImplementedError

    @classmethod
    def _add_arguments(cls, parser):
        raise NotImplementedError

    @classmethod
    def _add_registryhost_option(cls, parser):
        parser.add_argument("-H", "--registry-host", default=None, help=argparse.SUPPRESS)
        parser.add_argument("-k", "--insecure", action="store_true", default=False,
                            help="turn off verification of the https certificate")
        parser.add_argument("--cacert", default=None,
                            help="CA certificate to verify peer against (SSL)")

    @classmethod
    def _add_output_option(cls, parser):
        parser.add_argument("--output", default=cls.output_default, choices=[
            'text', 'none', 'json', 'yaml'], help="output format")

    @classmethod
    def _add_mediatype_option(cls, parser, default="-", required=False):
        default = os.getenv("APPR_DEFAULT_MEDIA_TYPE", default)

        if default is not None:
            required = False

        parser.add_argument(
            "-t", "--media-type", default=default, required=required,
            help='package format: [kpm, kpm-compose, helm, docker-compose, kubernetes, appr]')

    @classmethod
    def _add_packagename_option(cls, parser):
        parser.add_argument('package', nargs=1, default=None, action=PackageName,
                            help="package-name")

    @classmethod
    def _add_packagesplit_option(cls, parser):
        parser.add_argument('package', nargs="?", default=None, action=PackageSplit,
                            help="registry-host.com/namespace/name")

    @classmethod
    def _add_packageversion_option(cls, parser):
        parser.add_argument("-v", "--version", help="package VERSION", default='default')

    @classmethod
    def _add_registryhost_arg(cls, parser):
        parser.add_argument("registry_host", nargs=1, action=RegistryHost, help='registry API url')
        parser.add_argument("-k", "--insecure", action="store_true", default=False,
                            help="turn off verification of the https certificate")
        parser.add_argument("--cacert", nargs='?', default=None,
                            help="CA certificate to verify peer against (SSL)")
