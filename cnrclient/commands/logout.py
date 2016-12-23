from cnrclient.commands.command_base import CommandBase
from cnrclient.auth import CnrAuth


class LogoutCmd(CommandBase):
    name = 'logout'
    help_message = "logout"

    def __init__(self, options):
        super(LogoutCmd, self).__init__(options)
        self.status = None
        self.registry_host = options.registry_host

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_registryhost_arg(parser)

    def _call(self):
        CnrAuth().delete_token(self.registry_host)
        self.status = "Logout complete"
        if self.registry_host != '*':
            self.status += " from %s" % self.registry_host

    def _render_dict(self):
        return {"status": self.status, 'host': self.registry_host}

    def _render_console(self):
        return " >>> %s" % self.status
