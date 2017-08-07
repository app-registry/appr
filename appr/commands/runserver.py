from __future__ import absolute_import, division, print_function

from appr.api.gevent_app import GeventApp
from appr.commands.command_base import CommandBase


class RunServerCmd(CommandBase):
    name = 'run-server'
    help_message = 'Run the registry server (with gunicorn)'
    parse_unknown = False

    def __init__(self, options, unknown=None):
        super(RunServerCmd, self).__init__(options)
        self.options = options
        self.status = {}

    def _call(self):
        GeventApp(self.options).run()

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument("-p", "--port", nargs="?", default=5000, type=int,
                            help="server port listen")
        parser.add_argument("-b", "--bind", nargs="?", default="0.0.0.0",
                            help="server bind address")
        parser.add_argument("--db-class", nargs="?", default="filesystem",
                            help="db class for storage")

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self.status['result']
