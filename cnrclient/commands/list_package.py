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
        self.media_type = options.media_type
        self.result = None

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_arg(parser)
        cls._add_mediatype_option(parser, default=None)
        parser.add_argument("-u", "--user", default=None,
                            help="list packages owned by USER")
        parser.add_argument("-o", "--organization", default=None,
                            help="list ORGANIZATION packages")
        parser.add_argument("-s", "--search", default=None,
                            help="search query")

    def _call(self):
        client = self.RegistryClient(self.registry_host)
        params = {}
        if self.user:
            params['username'] = self.user
        if self.organization:
            params["namespace"] = self.organization
        if self.query:
            params['query'] = self.query
        if self.media_type:
            params['media_type'] = self.media_type

        self.result = client.list_packages(params)

    def _render_dict(self):
        return self.result

    def _render_console(self):
        return print_packages(self.result)
