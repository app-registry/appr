import pytest
from appr.formats.appr.manifest_jsonnet import ManifestJsonnet


@pytest.fixture()
def manifest(kubeui_package, package_dir):
    return ManifestJsonnet(kubeui_package)

@pytest.fixture()
def empty_manifest(empty_package_dir):
    return ManifestJsonnet(package=None)

@pytest.fixture()
def bad_manifest():
    return ManifestJsonnet(package=None)


def test_empty_resources(empty_manifest):
    assert empty_manifest.resources == []


def test_empty_variables(empty_manifest):
    assert empty_manifest.variables == {'namespace': 'default'}


def test_empty_package(empty_manifest):
    assert empty_manifest.package == {'expander': "jinja2"}


def test_empty_shards(empty_manifest):
    assert empty_manifest.shards is None


def test_empty_deploy(empty_manifest):
    assert empty_manifest.deploy == []


def test_package_name(manifest):
    assert manifest.package_name() == "kube-system_kube-ui_1.0.1"


def test_kubename(manifest):
    assert manifest.kubname() == "kube-system_kube-ui"


def test_load_from_path(manifest):
    m = ManifestJsonnet()
    assert m == manifest


def test_load_bad_manifest(bad_package_dir):
    import yaml
    with pytest.raises(yaml.YAMLError):
        ManifestJsonnet(package=None)
