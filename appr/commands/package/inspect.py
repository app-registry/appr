from __future__ import absolute_import, division, print_function
import yaml

from appr.commands.command_base import CommandBase
from appr.controller.models import PackageCr


class InspectCmd(CommandBase):
    name = 'inspect'
    help_message = "Browse package files"

    def __init__(self, options):
        super(InspectCmd, self).__init__(options)
        self.file = options.file
        self.tree = options.tree
        self.from_file = options.from_file
        self.namespace = options.namespace
        self.resource = options.resource
        self.status = {}
        self.package = None
        self.path = None

        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_output_option(parser)
        src_group = parser.add_mutually_exclusive_group()

        src_group.add_argument("--from-file", default=None, help="Read content from a local file")
        src_group.add_argument("resource", nargs='?', default=None,
                               help="kubernetes resource name")

        parser.add_argument("-n", "--namespace", default="default", help="kubernetes namespace")

        parser.add_argument('--tree', help="List files inside the package", action='store_true',
                            default=True)
        parser.add_argument('-f', '--file', help="Display a file", default=None)

    def _call(self):
        if self.from_file:
            with open(self.from_file, 'r') as fsource:
                source = yaml.safe_load(fsource)
        else:
            # TODO(ant31)
            source = "execute: kubectl get package %s -o yaml --export --namespace %s" % (
                self.resource, self.namespace)
        package_cr = PackageCr.load(source)
        self.package = package_cr.appr_package
        if self.file:
            self.result = self.package.file(self.file)
        elif self.tree:
            self.result = "\n".join(self.package.tree())
        else:
            self.result = self.package.manifest

    def _render_dict(self):
        return {"inspect": self.package, "output": self.result}

    def _render_console(self):
        return self.result
