import argparse
import os
import base64
import cnrclient.command
from cnrclient.pack import pack_kub
from cnrclient.utils import package_filename
from cnrclient.client import CnrClient as RegistryClient

from cnrclient.commands.command_base import CommandBase


class PushCmd(CommandBase):
    name = 'push'
    help_message = "push a package to the registry"

    def __init__(self, options):
        super(PushCmd, self).__init__(options)
        self.registry_host = options.registry_host
        self.force = options.force
        self.manifest = None
        self.media_type = options.media_type
        self.version = options.version
        self.package_name = options.name
        self.filter_files = True
        self.metadata = None
        self.prefix = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packageversion_option(parser)
        parser.add_argument('-n', "--name", default=None, action=cnrclient.command.PackageName, help="package-name")
        parser.add_argument("-f", "--force", action='store_true', default=False,
                            help="force push")

    def _push(self):
        client = RegistryClient(self.registry_host)
        filename = package_filename(self.package_name, self.version, self.media_type)
        # @TODO: Pack in memory
        kubepath = os.path.join(".", filename + ".tar.gz")
        pack_kub(kubepath, filter_files=self.filter_files, prefix=self.prefix)
        kubefile = open(kubepath, 'rb')
        body = {"name": self.package_name,
                "release": self.version,
                "metadata": self.metadata,
                "media_type": self.media_type,
                "blob": base64.b64encode(kubefile.read())}
        client.push(self.package_name, body, self.force)
        kubefile.close()
        os.remove(kubepath)

    def _init(self):
        self.filter_files = False
        if self.version is None or self.version == "default":
            raise argparse.ArgumentTypeError("Missing option: --version")
        if self.package_name is None:
            raise argparse.ArgumentTypeError("Missing option: --name")

    def _call(self):
        self._init()
        self._push()

    def _render_dict(self):
        return {"package": self.package_name,
                "version": self.version,
                "media_type": self.media_type}

    def _render_console(self):
        return "package: %s (%s) pushed" % (self.package_name, self.version)
