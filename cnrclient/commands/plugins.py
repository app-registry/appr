import os
import shutil
from cnrclient.commands.command_base import CommandBase
from cnrclient.utils import mkdir_p


LOCAL_DIR = os.path.dirname(__file__)


class PluginsCmd(CommandBase):
    name = 'plugins'
    help_message = "Install plugins"

    def __init__(self, options):
        super(PluginsCmd, self).__init__(options)
        self.plugin = options.plugin
        self.status = ""

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument("plugin", nargs='+',
                            help='plugin cmd')

    def _helm(self):
        default_path = os.getenv("HELM_HOME", "~/.helm")
        home = os.path.expanduser(default_path) + "/plugins/cnr"
        mkdir_p(home)
        source = os.path.join(LOCAL_DIR, "plugins/helm")
        files = [os.path.join(source, "plugin.yaml"),
                 os.path.join(source, "cnr.sh")]

        for f in files:
            shutil.copy(f, home)

        self.status = "helm plugin installed"

    def _call(self):
        if " ".join(self.plugin) == "install helm":
            self._helm()

    def _render_dict(self):
        return {"status": self.status}

    def _render_console(self):
        return self.status
