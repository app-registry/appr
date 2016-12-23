from cnrclient.commands.push import PushCmd
from cnrclient.commands.pull import PullCmd
from cnrclient.commands.version import VersionCmd
from cnrclient.commands.show import ShowCmd
from cnrclient.commands.login import LoginCmd
from cnrclient.commands.logout import LogoutCmd
from cnrclient.commands.channel import ChannelCmd
from cnrclient.commands.list_package import ListPackageCmd
from cnrclient.commands.delete_package import DeletePackageCmd


all_commands = {
    PushCmd.name: PushCmd,
    VersionCmd.name: VersionCmd,
    PullCmd.name: PullCmd,
    ShowCmd.name: ShowCmd,
    LoginCmd.name: LoginCmd,
    LogoutCmd.name: LogoutCmd,
    ChannelCmd.name: ChannelCmd,
    DeletePackageCmd.name: DeletePackageCmd,
    ListPackageCmd.name: ListPackageCmd,
}
