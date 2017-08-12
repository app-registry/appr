from __future__ import absolute_import, division, print_function

import argparse
import getpass
from builtins import input

from appr.commands.command_base import CommandBase, PackageSplit


class LoginCmd(CommandBase):
    name = 'login'
    help_message = "login"

    def __init__(self, options):
        super(LoginCmd, self).__init__(options)
        self.registry_host = options.registry_host
        self.signup = options.signup
        self.password = options.password
        self.email = options.email
        self.user = options.user
        self.status = None
        self.ssl_verify = options.cacert or not options.insecure

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
                            "If namespace and/or repo are passed, creds only requested for it")

        parser.add_argument("-s", "--signup", action='store_true', default=False,
                            help="Create a new account and login")
        parser.add_argument("-u", "--user", nargs="?", default=None, help="username")
        parser.add_argument("-p", "--password", nargs="?", default=None, help="password")
        parser.add_argument("-e", "--email", nargs="?", default=None, help="email for signup")

    def _call(self):
        client = self.RegistryClient(self.registry_host, requests_verify=self.ssl_verify)
        if self.user is not None:
            self.user = self.user
        else:
            self.user = input("Username: ")
        if self.password is not None:
            p1 = self.password
        else:
            p1 = getpass.getpass()

        if self.signup:
            if self.password is not None:
                p2 = p1
            else:
                p2 = getpass.getpass('Password confirmation: ')
            if self.email is not None:
                email = self.email
            else:
                email = input("Email: ")
            if p1 != p2:
                raise argparse.ArgumentError("password", message="Error: password mismatch")
            client.signup(self.user, p1, p2, email)
            self.status = "Registration complete"
        else:
            client.login(self.user, p1, scope=self.package)
            self.status = "Login succeeded"

    def _render_dict(self):
        return {"user": self.user, "status": self.status, "host": self.registry_host, "scope": self.package}

    def _render_console(self):
        return " >>> %s" % self.status
