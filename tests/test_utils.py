import os

import pytest
import appr.utils


def test_mkdirp_on_existing_dir(tmpdir):
    exists = str(tmpdir.mkdir("dir1"))
    appr.utils.mkdir_p(exists)
    assert os.path.exists(exists)


def test_mkdirp(tmpdir):
    path = os.path.join(str(tmpdir), "new/directory/tocreate")
    appr.utils.mkdir_p(path)
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
    assert appr.utils.parse_version(version) == expected


@pytest.mark.parametrize("package,expected", [
    ("localhost:5000/foo/bar", {"host": "localhost:5000", "namespace": "foo", "package": "bar", "version": "default"}),
    ("http://appr.io/foo/bar", {"host": "http://appr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("https://appr.io/foo/bar", {"host": "https://appr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("appr.io/foo/bar", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("appr.io/api/v1/foo/bar", {"host": "appr.io/api/v1", "namespace": "foo", "package": "bar", "version": "default"}),
    ("appr.io/foo/bar@3.4.4", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "@3.4.4"}),
    ("appr.io/foo/bar@v3.4.4", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "@v3.4.4"}),
    ("appr.io/foo/bar:stable", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": ":stable"}),
    ("appr.io/foo/bar:2.4-stable", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": ":2.4-stable"}),
    ("appr.io/foo/bar:2.4-stable+432.5.24-4324_5234", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": ":2.4-stable+432.5.24-4324_5234"}),
    ("appr.io/foo/bar@sha256:34245afe", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "@sha256:34245afe"}),
    ])
def test_parse_package_name(package, expected):
    assert appr.utils.parse_package_name(package) == expected


@pytest.mark.parametrize("package,expected", [
    ("foo/bar", {"host": None, "namespace": "foo", "package": "bar", "version": "default"}),
    ("bar/@24", {"host": "https://appr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("appr.io:stable", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "default"}),
    ("appr.io", {"host": "appr.io/api/v1", "namespace": "foo", "package": "bar", "version": "default"}),
    ("appr.io/foo@3.4.4", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "@3.4.4"}),
    ("appr.io/foo/bar@v^3.4.4", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "@v3.4.4"}),
    ("appr.io/foo/bar:@stable", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": ":stable"}),
    ("appr.io/foo/bar:2.4:stable", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": ":2.4:stable"}),
    ("appr.io/foo/bar@sha256:34245.afe", {"host": "appr.io", "namespace": "foo", "package": "bar", "version": "@sha256:34245afe"}),
    ])
def test_parse_bad_package_name(package, expected):
    with pytest.raises(ValueError):
        assert appr.utils.parse_package_name(package) == expected
