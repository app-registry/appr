from __future__ import absolute_import, division, print_function

from appr.commands.command_base import CommandBase
from appr.pack import ApprPackage


class InspectCmd(CommandBase):
    name = 'inspect'
    help_message = "Browse package files"

    def __init__(self, options):
        super(InspectCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.version = options.version
        self.version_parts = options.version_parts
        self.file = options.file
        self.tree = options.tree
        self.media_type = options.media_type
        self.result = None
        self.format = options.media_type
        self.ssl_verify = options.cacert or not options.insecure

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser, required=True)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument('--tree', help="List files inside the package", action='store_true',
                            default=True)
        parser.add_argument('-f', '--file', help="Display a file", default=None)

    def _call(self):
        client = self.RegistryClient(self.registry_host, requests_verify=self.ssl_verify)
        result = client.pull(self.package, version_parts=self.version_parts,
                             media_type=self.media_type)
        package = ApprPackage(result, b64_encoded=False)
        if self.file:
            self.result = package.file(self.file)
        elif self.tree:
            self.result = "\n".join(package.tree())
        else:
            self.result = package.manifest

    def _render_dict(self):
        return {"inspect": self.package, "output": self.result}

    def _render_console(self):
        return self.result
