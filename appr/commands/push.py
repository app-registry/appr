from __future__ import absolute_import, division, print_function

import argparse
import base64
import os
import tempfile

import requests

from appr.commands.command_base import CommandBase, PackageSplit
from appr.formats.helm.manifest_chart import ManifestChart
from appr.formats.appr.manifest_jsonnet import ManifestJsonnet
from appr.formats.utils import detect_format
from appr.pack import pack_kub
from appr.utils import package_filename


class PushCmd(CommandBase):
    name = 'push'
    help_message = "push a package to the registry"
    default_media_type = None

    def __init__(self, options):
        super(PushCmd, self).__init__(options)
        self.registry_host = options.registry_host
        self.force = options.force
        self.manifest = None
        self.media_type = options.media_type
        self.channel = options.channel
        self.version = options.version
        self.filter_files = True
        self.metadata = None
        self.prefix = None
        self.manifest_name = None
        self.package_name = options.package
        self.package_parts = options.package_parts
        self.pname = self.package_parts.get('package', None)
        self.namespace = self.package_parts.get('namespace', None)

        if self.namespace is None:
            self.namespace = options.ns

        self.version_parts = options.version_parts

        if self.version == "default":
            self.version = None

        self.ssl_verify = options.cacert or not options.insecure
        self.status = ''

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser, cls.default_media_type, required=False)
        cls._add_packageversion_option(parser)
        parser.add_argument("--ns", "--namespace", default=None, help=argparse.SUPPRESS)
        parser.add_argument("-f", "--force", action='store_true', default=False, help="force push")
        parser.add_argument("-c", "--channel", default=None, help="Set a channel")
        parser.add_argument("--version-parts", default={}, help=argparse.SUPPRESS)
        parser.add_argument("--package-parts", default={}, help=argparse.SUPPRESS)
        parser.add_argument('package', nargs='?', default=None, action=PackageSplit,
                            help="repository dest")

    def _push(self):
        client = self.RegistryClient(self.registry_host, requests_verify=self.ssl_verify)
        filename = package_filename(self.package_name, self.version, self.media_type)
        kubepath = os.path.join(tempfile.gettempdir(), filename + ".tar.gz")
        pack_kub(kubepath, filter_files=self.filter_files, prefix=self.prefix)
        kubefile = open(kubepath, 'rb')
        body = {
            "manifest_name": self.manifest_name,
            "name": self.package_name,
            "release": self.version,
            "metadata": self.metadata,
            "media_type": self.media_type,
            "blob": base64.b64encode(kubefile.read())}
        try:
            client.push(self.package_name, body, self.force)
            self.status = "package: %s (%s | %s) pushed\n" % (self.package_name, self.version,
                                                              self.media_type)
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
        self.manifest_name = self.manifest.name
        if self.pname is None:
            self.pname = self.manifest.name
        self.prefix = self.pname
        self.filter_files = False
        if self.namespace is None:
            raise argparse.ArgumentTypeError("Missing option: --namespace")
        self.package_name = "%s/%s" % (self.namespace, self.pname)
        if self.version is None:
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
        self.filter_files = False
        self.manifest = ManifestJsonnet()
        ns, name = self.manifest.package['name'].split("/")
        if not self.namespace:
            self.namespace = ns
        if not self.pname:
            self.pname = name
        self.package_name = "%s/%s" % (self.namespace, self.pname)
        if not self.version or self.version == "default":
            self.version = self.manifest.package['version']
        self.metadata = self.manifest.metadata()

    def _init(self):
        if self.media_type is None:
            self.media_type = detect_format(".").media_type
        if self.media_type in ["kpm", "kpm-compose"]:
            self._kpm()
        elif self.media_type in ['helm', 'chart']:
            self._chart()
        else:
            self._all_formats()

    def _call(self):
        self._init()
        self._push()

    def _render_dict(self):
        return {
            "manifest_name": self.manifest_name,
            "package": self.package_name,
            "version": self.version,
            "media_type": self.media_type,
            "channel": self.channel}

    def _render_console(self):
        return self.status
