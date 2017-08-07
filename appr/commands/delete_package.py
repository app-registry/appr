from __future__ import absolute_import, division, print_function

from appr.commands.command_base import CommandBase


class DeletePackageCmd(CommandBase):
    name = 'delete-package'
    help_message = 'delete package from the registry'

    def __init__(self, options):
        super(DeletePackageCmd, self).__init__(options)
        self.package = options.package
        self.registry_host = options.registry_host
        self.version = options.version
        self.media_type = options.media_type
        self.result = None
        self.ssl_verify = options.cacert or not options.insecure

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        cls._add_mediatype_option(parser)
        cls._add_packagename_option(parser)
        cls._add_packageversion_option(parser)

    def _call(self):
        client = self.RegistryClient(self.registry_host, requests_verify=self.ssl_verify)
        self.result = client.delete_package(self.package, version=self.version,
                                            media_type=self.media_type)

    def _render_dict(self):
        return self.result

    def _render_console(self):
        return "Deleted package: %s - %s" % (self.result['package'], self.result['release'])
