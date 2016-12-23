from cnrclient.client import CnrClient as RegistryClient
from cnrclient.display import print_packages
from cnrclient.commands.command_base import CommandBase


class ListPackageCmd(CommandBase):
    name = 'list'
    help_message = "list packages"

    def __init__(self, options):
        super(ListPackageCmd, self).__init__(options)
        self.registry_host = options.registry_host
        self.user = options.user
        self.organization = options.organization
        self.query = options.search
        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_arg(parser)
        parser.add_argument("-u", "--user", default=None,
                            help="list packages owned by USER")
        parser.add_argument("-o", "--organization", default=None,
                            help="list ORGANIZATION packages")
        parser.add_argument("-s", "--search", default=None,
                            help="search query")

    def _call(self):
        client = RegistryClient(self.registry_host)
        self.result = client.list_packages(user=self.user, organization=self.organization,
                                           text_search=self.query)

    def _render_dict(self):
        return self.result

    def _render_console(self):
        return print_packages(self.result)
