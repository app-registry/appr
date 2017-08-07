from __future__ import absolute_import, division, print_function

import os

from appr.commands.command_base import CommandBase
from appr.config import ApprConfig

LOCAL_DIR = os.path.dirname(__file__)


class ConfigCmd(CommandBase):
    name = 'config'
    help_message = "Install config"

    def __init__(self, options):
        super(ConfigCmd, self).__init__(options)
        self.plugin = options.plugin
        self.status = {}

    @classmethod
    def add_alias(cls, options):
        alias = options.alias
        target = options.host
        config = ApprConfig()
        config.add_registry_alias(alias, target)

    @classmethod
    def _add_arguments(cls, parser):
        sub = parser.add_subparsers()
        command = sub.add_parser('alias')
        command.add_argument("alias", help="Registry alias name")
        command.add_argument("host", help="url")
        command.set_defaults(func=cls.add_alias)

    def _call(self):
        pass

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self._render_yaml()
