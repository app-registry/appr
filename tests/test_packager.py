import pytest
import os.path

from cnr.packager import unpack_app
import hashlib


TAR_MD5SUM = "8ccd8af6ef21af7309839f1c521b6354"
KUBEUI_FILES = ["manifest.yaml",
                "README.md",
                "templates/kube-ui-rc.yaml",
                "templates/kube-ui-svc.yaml"]


def _check_app(path):
    for f in KUBEUI_FILES:
        assert os.path.exists(os.path.join(str(path), f))


def test_unpack_app(pack_tar, tmpdir):
    unpack_app(pack_tar, str(tmpdir))
    _check_app(str(tmpdir))


def test_extract(kubeui_package, tmpdir):
    d = tmpdir.mkdir("extract")
    kubeui_package.extract(str(d))
    _check_app(str(d))


def test_pack(kubeui_package, tmpdir):
    d = str(tmpdir.mkdir("pack")) + "/kube-ui.tar"
    kubeui_package.pack(d)
    assert hashlib.md5(open(d, "r").read()).hexdigest() == TAR_MD5SUM


def test_tree(kubeui_package):
    files = kubeui_package.tree()
    assert sorted(files) == sorted(KUBEUI_FILES)


def test_tree_filter(kubeui_package):
    files = kubeui_package.tree("templates")
    assert sorted(files) == sorted(["templates/kube-ui-rc.yaml", "templates/kube-ui-svc.yaml"])


def test_file(kubeui_package, data_dir):
    manifest = kubeui_package.file("manifest.yaml")
    assert manifest == open(data_dir + "/kube-ui/manifest.yaml", "r").read()
