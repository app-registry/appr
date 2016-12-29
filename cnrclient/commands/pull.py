import os
from cnrclient.utils import parse_version
from cnrclient.pack import CnrPackage
from cnrclient.commands.command_base import CommandBase


class PullCmd(CommandBase):
    name = 'pull'
    help_message = "download a package"

    def __init__(self, options):
        super(PullCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.version = options.version
        self.parsed_version = parse_version(self.version)['value']
        self.dest = options.dest
        self.media_type = options.media_type
        self.tarball = options.tarball
        self.path = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument("--dest", default="/tmp",
                            help="directory used to extract resources")
        parser.add_argument("--tarball", action="store_true", default=False,
                            help="download the tar.gz")

    def _call(self):
        client = self.RegistryClient(self.registry_host)
        pullpack = client.pull_json(self.package, version=self.version, media_type=self.media_type)
        package = CnrPackage(pullpack['blob'], b64_encoded=True)
        filename = pullpack['filename']
        # package_filename(self.package, self.parsed_version, self.media_type)
        self.path = os.path.join(self.dest, filename)
        if self.tarball:
            with open(self.path, 'wb') as tarfile:
                tarfile.write(package.blob)
        else:
            self.path = self.path.split(".tar.gz")[0]
            package.extract(self.path)

    def _render_dict(self):
        return {"pull": self.package,
                "media_type": self.media_type,
                "version": self.version,
                "path": self.path}

    def _render_console(self):
        return "Pull package: %s... \n%s" % (self.package, self.path)
