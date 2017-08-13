from __future__ import absolute_import, division, print_function
import os
from appr.commands.command_base import CommandBase
from appr.display import print_package_info


class ShowCmd(CommandBase):
    name = 'show'
    help_message = "print the package manifest"
    default_media_type = None

    def __init__(self, options):
        super(ShowCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.version = options.version
        self.verbose = options.wide
        self.media_type = options.media_type
        if options.media_type == self.default_media_type:
            self.media_type = os.getenv("APPR_DEFAULT_MEDIA_TYPE", self.default_media_type)

        self.result = None
        self.ssl_verify = options.cacert or not options.insecure

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)
        cls._add_mediatype_option(parser, default=cls.default_media_type, required=False)
        parser.add_argument("-w", "--wide", help="Extend display informations",
                            action="store_true", default=False)

    def _call(self):
        client = self.RegistryClient(self.registry_host, requests_verify=self.ssl_verify)
        self.result = client.show_package(self.package, version=self.version,
                                          media_type=self.media_type)

    def _render_dict(self):
        return self.result

    def _render_console(self):
        return "Info: %s\n\n" % self.package + print_package_info(self.result, self.verbose)
