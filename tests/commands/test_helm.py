import pytest
import requests_mock
from appr.commands.helm import HelmCmd


def get_helmcmd(cli_parser, args=[]):
    options = cli_parser.parse_args(["helm"] + args)
    return HelmCmd(options)


def test_helm_init(cli_parser):
    helmcmd = get_helmcmd(cli_parser, ["install", "kpm.sh/foo/bar"])
    assert helmcmd.args_options.media_type == "helm"
    assert helmcmd.args_options.registry_host == "kpm.sh"
    assert HelmCmd.name == "helm"
