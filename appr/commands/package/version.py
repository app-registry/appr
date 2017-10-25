from __future__ import absolute_import, division, print_function

import appr
from appr.commands.command_base import CommandBase


class VersionCmd(CommandBase):
    name = 'version'
    help_message = "show version"

    def __init__(self, options):
        super(VersionCmd, self).__init__(options)
        self.client_version = None

    def _cli_version(self):
        return appr.__version__

    def _version(self):
        return {"client-version": self._cli_version()}

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_output_option(parser)

    def _call(self):
        version = self._version()
        self.client_version = version['client-version']

    def _render_dict(self):
        return {"client-version": self.client_version}

    def _render_console(self):
        return "\n".join([
            "Client-version: %s" % self.client_version])
