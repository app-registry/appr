from __future__ import absolute_import, division, print_function

from appr.auth import ApprAuth
from appr.commands.command_base import CommandBase, PackageSplit


class LogoutCmd(CommandBase):
    name = 'logout'
    help_message = "logout"

    def __init__(self, options):
        super(LogoutCmd, self).__init__(options)
        self.status = None
        self.registry_host = options.registry_host
        self.package_parts = options.package_parts
        pname = self.package_parts.get('package', None)
        namespace = self.package_parts.get('namespace', None)
        self.package = None
        if pname:
            self.package = "%s/%s" % (namespace, pname)
        elif namespace:
            self.package = namespace

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_option(parser)
        parser.add_argument('registry', nargs='?', default=None, action=PackageSplit,
                            help="registry url: quay.io[/namespace][/repo]\n" +
                            "If namespace and/or repo are passed, creds only logout for them")

    def _call(self):
        client = self.RegistryClient(self.registry_host)
        ApprAuth().delete_token(client.host, scope=self.package)
        self.status = "Logout complete"
        if self.registry_host != '*':
            self.status += " from %s" % self.registry_host

    def _render_dict(self):
        return {"status": self.status, 'host': self.registry_host, "scope": self.package}

    def _render_console(self):
        return " >>> %s" % self.status
