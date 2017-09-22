from __future__ import absolute_import, division, print_function

import hashlib
import os.path

import pytest

from appr import SYSTEM
from appr.pack import unpack_kub, ignore

TAR_MD5SUM = {
    'darwin': "8ccd8af6ef21af7309839f1c521b6354",
    'linux': "8ccd8af6ef21af7309839f1c521b6354",
    'windows': '20bf57e5d5dec33e51bf1f04bfde4367'
}

KUBEUI_FILES = [
    "manifest.yaml", "README.md", "templates/kube-ui-rc.yaml", "templates/kube-ui-svc.yaml"
]


def _check_app(path):
    for f in KUBEUI_FILES:
        assert os.path.exists(os.path.join(str(path), f))


def test_unpack_kub(pack_tar, tmpdir):
    unpack_kub(pack_tar, str(tmpdir))
    _check_app(str(tmpdir))


def test_extract(kubeui_package, tmpdir):
    d = tmpdir.mkdir("extract")
    kubeui_package.extract(str(d))
    _check_app(str(d))


def test_pack(kubeui_package, tmpdir):
    d = str(tmpdir.mkdir("pack")) + "/kube-ui.tar"
    kubeui_package.pack(d)
    assert hashlib.md5(open(d, "r").read()).hexdigest() == TAR_MD5SUM[SYSTEM]


def test_tree(kubeui_package):
    files = kubeui_package.tree()
    assert sorted(files) == sorted(KUBEUI_FILES)


def test_tree_filter(kubeui_package):
    files = kubeui_package.tree("templates")
    assert sorted(files) == sorted(["templates/kube-ui-rc.yaml", "templates/kube-ui-svc.yaml"])


def test_file(kubeui_package, data_dir):
    manifest = kubeui_package.file("manifest.yaml")
    assert manifest == open(data_dir + "/kube-ui/manifest.yaml", "r").read()


@pytest.mark.parametrize(
    "pattern,file_path,expected",
    [
        ('helm.txt', "helm.txt", True),
        ('helm.*', "helm.txt", True),
        ('helm.*', "rudder.txt", False),
        ('*.txt', "tiller.txt", True),
        ('*.txt', "cargo/a.txt", True),
        ('cargo/*.txt', "cargo/a.txt", True),
        ('cargo/*.*', "cargo/a.txt", True),
        ('cargo/*.txt', "mast/a.txt", False),
        ('ru[c-e]?er.txt', "rudder.txt", True),
        ('templates/.?*', "templates/.dotfile", True),

        # Directory tests
        (".git", ".git/toto", True),
        (".git", ".git/toto/titi", True),
        ('cargo/', "cargo/", True),
        ('cargo/', "cargo/a.txt", True),
        ('cargo/', "mast/", False),
        ('helm.txt/', "helm.txt", False),
        # // Negation tests
        ('!helm.txt', "helm.txt", False),
        ('helm.txt\n!helm.txt', "helm.txt", False),
        ('*\n!helm.txt', "tiller.txt", True),
        ('*\n!*.txt', "cargo", True),
        ('*\n!cargo/', "mast/a", True),
        # Absolute path tests
        ('/a.txt', "a.txt", True),
        ('/a.txt', "cargo/a.txt", False),
        ('/cargo/a.txt', "cargo/a.txt", True),
    ])
def test_ignore(pattern, file_path, expected):
    assert ignore(pattern, file_path) is expected
