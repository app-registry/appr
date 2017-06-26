import argparse
import gunicorn.config

from appr.commands.command_base import CommandBase
from appr.api.gunicorn_app import GunicornApp


class RunServerCmd(CommandBase):
    name = 'run-server'
    help_message = 'Run the registry server (with gunicorn)'
    parse_unknown = False

    def __init__(self, options, unknown=None):
        super(RunServerCmd, self).__init__(options)
        self.options = options
        self.status = {}

    def _call(self):
        GunicornApp(self.options).run()

    @classmethod
    def _add_arguments(cls, parser):
        gconf = gunicorn.config.Config()
        parser.add_argument("args", nargs="*", help=argparse.SUPPRESS)

        keys = sorted(gconf.settings, key=gconf.settings.__getitem__)
        for k in keys:
            gconf.settings[k].add_option(parser)

    def _render_dict(self):
        return self.status

    def _render_console(self):
        return self.status['result']
