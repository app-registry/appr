from __future__ import absolute_import, division, print_function
import yaml
from appr.commands.command_base import CommandBase
from appr.controller.models import PackageCr


class ExtractCmd(CommandBase):
    name = 'extract'
    help_message = "Fetch and extract content of a Package"
    output_default = 'yaml'

    def __init__(self, options):
        super(ExtractCmd, self).__init__(options)
        self.dest = options.dest
        self.tarball = options.tarball
        self.from_file = options.from_file
        self.digest = options.digest
        self.namespace = options.namespace
        self.resource = options.resource
        self.status = {}
        self.package = None
        self.path = None

    def _call(self):
        if self.from_file:
            with open(self.from_file, 'r') as fsource:
                source = yaml.safe_load(fsource)
            self.package = PackageCr.load(source)
        elif self.digest:
            self.package = PackageCr.find({'digest': self.digest[0:10]}, self.namespace)
        else:
            self.package = PackageCr.get(self.resource, self.namespace)

        self.path = self.package.extract(self.dest, self.tarball)

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_output_option(parser)
        src_group = parser.add_mutually_exclusive_group()
        src_group.add_argument("--digest", default=None, help="get by digest")
        src_group.add_argument("--from-file", default=None, help="Read content from a local file")
        src_group.add_argument("resource", nargs='?', default=None,
                               help="kubernetes resource name")

        parser.add_argument("-n", "--namespace", default="default", help="kubernetes namespace")
        parser.add_argument("--dest", default="./", help="directory used to extract resources")
        parser.add_argument("--tarball", action="store_true", default=False,
                            help="extract as a tar.gz")

    def _render_dict(self):
        return {
            "pull": self.package.name,
            "media_type": self.package.media_type,
            "version": self.package.version,
            "path": self.path
        }

    def _render_console(self):
        return "Pull package: %s... \n%s" % (self.package.name, self.path)
