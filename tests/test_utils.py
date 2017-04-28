import os

import pytest
import cnrclient.utils


def test_mkdirp_on_existing_dir(tmpdir):
    exists = str(tmpdir.mkdir("dir1"))
    cnrclient.utils.mkdir_p(exists)
    assert os.path.exists(exists)


def test_mkdirp(tmpdir):
    path = os.path.join(str(tmpdir), "new/directory/tocreate")
    cnrclient.utils.mkdir_p(path)
    assert os.path.exists(path)


@pytest.mark.parametrize("version,expected", [
    ("@v2.3.0", {"key": "version", "value": "v2.3.0"}),
    (":v2.3.0", {"key": "channel", "value": "v2.3.0"}),
    (":stable", {"key": "channel", "value": "stable"}),
    ("@stable", {"key": "version", "value": "stable"}),
    ("@stable", {"key": "version", "value": "stable"}),
    ("@sha256:4242a432aehf", {"key": "digest", "value": "4242a432aehf"}),
    ("@sha256-4242", {"key": "version", "value": "sha256-4242"}),
    ("@sha256-4242", {"key": "version", "value": "sha256-4242"}),
    ])
def test_parse_version(version, expected):
    assert cnrclient.utils.parse_version(version) == expected


@pytest.mark.parametrize("package,expected", [
    ("localhost:5000/foo/bar", {"host": "localhost:5000", "namespace": "foo", "package": "bar", "version": "default"}),
    ("http://cnr.io/foo/bar", {"host": "http://cnr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("https://cnr.io/foo/bar", {"host": "https://cnr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("cnr.io/foo/bar", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("cnr.io/api/v1/foo/bar", {"host": "cnr.io/api/v1", "namespace": "foo", "package": "bar", "version": "default"}),
    ("cnr.io/foo/bar@3.4.4", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "@3.4.4"}),
    ("cnr.io/foo/bar@v3.4.4", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "@v3.4.4"}),
    ("cnr.io/foo/bar:stable", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": ":stable"}),
    ("cnr.io/foo/bar:2.4-stable", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": ":2.4-stable"}),
    ("cnr.io/foo/bar:2.4-stable+432.5.24-4324_5234", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": ":2.4-stable+432.5.24-4324_5234"}),
    ("cnr.io/foo/bar@sha256:34245afe", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "@sha256:34245afe"}),
    ])
def test_parse_package_name(package, expected):
    assert cnrclient.utils.parse_package_name(package) == expected


@pytest.mark.parametrize("package,expected", [
    ("foo/bar", {"host": None, "namespace": "foo", "package": "bar", "version": "default"}),
    ("bar/@24", {"host": "https://cnr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("cnr.io:stable", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("cnr.io", {"host": "cnr.io/api/v1", "namespace": "foo", "package": "bar", "version": "default"}),
    ("cnr.io/foo@3.4.4", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "@3.4.4"}),
    ("cnr.io/foo/bar@v^3.4.4", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "@v3.4.4"}),
    ("cnr.io/foo/bar:@stable", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": ":stable"}),
    ("cnr.io/foo/bar:2.4:stable", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": ":2.4:stable"}),
    ("cnr.io/foo/bar@sha256:34245.afe", {"host": "cnr.io", "namespace": "foo", "package": "bar", "version": "@sha256:34245afe"}),
    ])
def test_parse_bad_package_name(package, expected):
    with pytest.raises(ValueError):
        assert cnrclient.utils.parse_package_name(package) == expected
