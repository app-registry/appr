import pytest
import requests_mock
from appr.commands.inspect import InspectCmd
from appr.client import DEFAULT_PREFIX


def get_inspectcmd(cli_parser, args=[]):
    options = cli_parser.parse_args(["inspect"] + args)
    return InspectCmd(options)


def test_inspect_init(cli_parser):
    inspectcmd = get_inspectcmd(cli_parser, ["kpm.sh/foo/bar", "-t", "helm"])
    assert inspectcmd.version == "default"
    assert inspectcmd.registry_host == "kpm.sh"
    assert InspectCmd.name == "inspect"


def test_inspect_tree(cli_parser, package_blob, capsys):
    inspectcmd = get_inspectcmd(cli_parser, ["kpm.sh/foo/bar@1.0.0", "-t", "helm", "--tree"])
    with requests_mock.mock() as m:
        response = package_blob
        m.get("https://kpm.sh" + DEFAULT_PREFIX + "/api/v1/packages/foo/bar/1.0.0/helm/pull", content=response)
        inspectcmd.exec_cmd()
        out, err = capsys.readouterr()
        default_out = ["README.md", "manifest.yaml", "templates/rocketchat-rc.yml", "templates/rocketchat-svc.yml\n"]
        default_out.sort()
        assert out == "\n".join(default_out)


def test_inspect_no_media_type(cli_parser, package_blob, capsys):
    with pytest.raises(SystemExit) as exc:
        inspectcmd = get_inspectcmd(cli_parser, ["kpm.sh/foo/bar@1.0.0", "--tree"])
    assert exc.value.code == 2


def test_inspect_default(cli_parser, package_blob, capsys):
    """ Default is the tree view """
    inspectcmd = get_inspectcmd(cli_parser, ["kpm.sh/foo/bar@1.0.0", "-t", "helm", "--tree"])
    inspectcmd_default_file = get_inspectcmd(cli_parser, ["kpm.sh/foo/bar@1.0.0", "-t", "helm"])
    with requests_mock.mock() as m:
        response = package_blob
        m.get("https://kpm.sh" + DEFAULT_PREFIX + "/api/v1/packages/foo/bar/1.0.0/helm/pull", content=response)
        inspectcmd.exec_cmd()
        out, err = capsys.readouterr()
        inspectcmd_default_file.exec_cmd()
        default_out, default_err = capsys.readouterr()
        assert out == default_out


def test_inspect_file(cli_parser, package_blob, capsys):
    inspectcmd = get_inspectcmd(cli_parser, ["kpm.sh/foo/bar@1.0.0", "-t", "helm", "--file", "README.md"])
    with requests_mock.mock() as m:
        response = package_blob
        m.get("https://kpm.sh" + DEFAULT_PREFIX + "/api/v1/packages/foo/bar/1.0.0/helm/pull", content=response)
        inspectcmd.exec_cmd()
        out, err = capsys.readouterr()
        readme = "\nrocketchat\n===========\n\n# Install\n\nkpm install rocketchat\n\n"
        assert out == readme + "\n"
        assert inspectcmd._render_dict() == {'inspect': 'foo/bar', 'output': readme}
