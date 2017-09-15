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

@pytest.mark.jsonnet
def test_empty_resources(empty_manifest):
    assert empty_manifest.resources == []

@pytest.mark.jsonnet
def test_empty_variables(empty_manifest):
    assert empty_manifest.variables == {'namespace': 'default'}

@pytest.mark.jsonnet
def test_empty_package(empty_manifest):
    assert empty_manifest.package == {'expander': "jinja2"}


@pytest.mark.jsonnet
def test_empty_shards(empty_manifest):
    assert empty_manifest.shards is None


@pytest.mark.jsonnet
def test_empty_deploy(empty_manifest):
    assert empty_manifest.deploy == []


@pytest.mark.jsonnet
def test_package_name(manifest):
    assert manifest.package_name() == "kube-system_kube-ui_1.0.1"


@pytest.mark.jsonnet
def test_kubename(manifest):
    assert manifest.kubname() == "kube-system_kube-ui"


@pytest.mark.jsonnet
def test_load_from_path(manifest):
    m = ManifestJsonnet()
    assert m == manifest


@pytest.mark.jsonnet
def test_load_bad_manifest(bad_package_dir):
    import yaml
    with pytest.raises(yaml.YAMLError):
        ManifestJsonnet(package=None)
