import os
import json
import argparse
from appr.render_jsonnet import RenderJsonnet
from appr.commands.command_base import CommandBase, LoadVariables


class JsonnetCmd(CommandBase):
    name = 'jsonnet'
    help_message = "Resolve a jsonnet file"

    def __init__(self, options):
        super(JsonnetCmd, self).__init__(options)
        self.namespace = options.namespace
        self.variables = options.variables
        self.filepath = options.filepath[0]
        self.extra_libs = options.lib_dir
        self.raw = options.raw
        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument("--namespace", help="kubernetes namespace", default='default')
        parser.add_argument("-x", "--variables", help="variables", default={},
                            action=LoadVariables)
        parser.add_argument('filepath', nargs=1, help="Fetch package from the registry")
        parser.add_argument('--raw', action="store_true", default=False, help=argparse.SUPPRESS)
        parser.add_argument('-J', '--lib-dir', action='append', default=[],
                            help="Specify an additional library search dir")

    def _call(self):
        r = RenderJsonnet(manifestpath=self.filepath, lib_dirs=self.extra_libs)
        if os.path.basename(self.filepath) == "manifest.jsonnet" and not self.raw:
            namespace = self.namespace
            self.variables['namespace'] = namespace
            tla_codes = {"params": json.dumps({"variables": self.variables})}
        else:
            tla_codes = self.variables
        p = open(self.filepath).read()
        self.result = r.render_jsonnet(p, tla_codes=tla_codes)

    def _render_dict(self):
        return self.result

    def _render_console(self):
        return json.dumps(self._render_dict(), indent=2, separators=(',', ': '))
