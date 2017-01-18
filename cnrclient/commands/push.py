import argparse
import os
import base64

import requests

from cnrclient.pack import pack_kub
from cnrclient.utils import package_filename
from cnrclient.commands.command_base import CommandBase
from cnrclient.formats.helm.manifest_chart import ManifestChart
from cnrclient.formats import detect_format


class PushCmd(CommandBase):
    name = 'push'
    help_message = "push a package to the registry"
    default_media_type = None

    def __init__(self, options):
        super(PushCmd, self).__init__(options)
        self.registry_host = options.registry_host
        self.force = options.force
        self.manifest = None
        self.namespace = options.ns
        self.media_type = options.media_type
        self.channel = options.channel
        self.version = options.version
        self.package_name = options.name
        self.filter_files = True
        self.metadata = None
        self.prefix = None
        self.pname = None
        self.status = ''

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_arg(parser)
        cls._add_mediatype_option(parser, cls.default_media_type, required=False)
        cls._add_packageversion_option(parser)
        parser.add_argument("-f", "--force", action='store_true', default=False,
                            help="force push")
        parser.add_argument("--ns", "--namespace", default=None,
                            help="package namespace")
        parser.add_argument("--name", default=None,
                            help=argparse.SUPPRESS)
        parser.add_argument("-c", "--channel", default=None,
                            help="Set a channel")

    def _push(self):
        client = self.RegistryClient(self.registry_host)
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
        try:
            client.push(self.package_name, body, self.force)
            self.status = "package: %s (%s | %s) pushed\n" % (self.package_name, self.version, self.media_type)
        except requests.exceptions.RequestException as exc:
            if not (self.channel and exc.response.status_code in [409, 400]):
                raise
        kubefile.close()
        os.remove(kubepath)
        if self.channel:
            client.create_channel_release(self.package_name, self.channel, self.version)
            self.status += ">>> Release '%s' added to '%s'" % (self.version, self.channel)

    def _chart(self):
        self.manifest = ManifestChart()
        if self.pname is None:
            self.pname = self.manifest.name
        self.prefix = self.pname
        self.filter_files = False
        if self.namespace is None:
            raise argparse.ArgumentTypeError("Missing option: --namespace")
        self.package_name = "%s/%s" % (self.namespace, self.pname)
        self.version = self.manifest.version
        self.metadata = self.manifest.metadata()

    def _all_formats(self):
        self.filter_files = False
        if self.version is None or self.version == "default":
            raise argparse.ArgumentTypeError("Missing option: --version")
        if self.package_name is None:
            raise argparse.ArgumentTypeError("Missing option: --name")
        self.namespace, self.pname = self.package_name.split("/")

    def _kpm(self):
        raise NotImplementedError

    def _init(self):
        if self.media_type is None:
            self.media_type = detect_format(".").media_type
        if self.media_type in ["kpm", "kpm-compose"]:
            self._kpm()
        if self.media_type in ["docker-compose"]:
            self._all_formats()
        elif self.media_type in ['helm', 'chart']:
            self._chart()

    def _call(self):
        self._init()
        self._push()

    def _render_dict(self):
        return {"package": self.package_name,
                "version": self.version,
                "media_type": self.media_type,
                "channel": self.channel}

    def _render_console(self):
        return self.status
