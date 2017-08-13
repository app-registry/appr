from __future__ import absolute_import, division, print_function

import os

from appr.commands.command_base import CommandBase
from appr.pack import ApprPackage


class PullCmd(CommandBase):
    name = 'pull'
    help_message = "download a package"

    def __init__(self, options):
        super(PullCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.version = options.version
        self.version_parts = options.version_parts
        self.dest = options.dest
        self.media_type = options.media_type
        if options.media_type is self.default_media_type:
            self.media_type = os.getenv("APPR_DEFAULT_MEDIA_TYPE", self.default_media_type)

        self.tarball = options.tarball
        self.path = None
        self.ssl_verify = options.cacert or not options.insecure

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument("--dest", default="./", help="directory used to extract resources")
        parser.add_argument("--tarball", action="store_true", default=False,
                            help="download the tar.gz")

    def _call(self):
        client = self.RegistryClient(self.registry_host, requests_verify=self.ssl_verify)
        pullpack = client.pull_json(self.package, version_parts=self.version_parts,
                                    media_type=self.media_type)
        self.media_type = pullpack.get('media_type', '-')
        package = ApprPackage(pullpack['blob'], b64_encoded=True)
        filename = pullpack['filename']
        self.path = os.path.join(self.dest, filename)
        if self.tarball:
            with open(self.path, 'wb') as tarfile:
                tarfile.write(package.blob)
        else:
            self.path = self.path.split(".tar.gz")[0]
            package.extract(self.path)

    def _render_dict(self):
        return {
            "pull": self.package,
            "media_type": self.media_type,
            "version": self.version,
            "path": self.path}

    def _render_console(self):
        return "Pull package: %s... \n%s" % (self.package, self.path)
