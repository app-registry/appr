import pytest

from appr.plugins.helm import parse_version, Helm


@pytest.mark.parametrize("version,expected", [
    ("v2.3.0", {
        "key": "version",
        "value": "v2.3.0"
    }),
    (":v2.3.0", {
        "key": "channel",
        "value": "v2.3.0"
    }),
    (":stable", {
        "key": "channel",
        "value": "stable"
    }),
    ("stable", {
        "key": "version",
        "value": "stable"
    }),
    ("stable", {
        "key": "version",
        "value": "stable"
    }),
    ("sha256:4242a432aehf", {
        "key": "digest",
        "value": "4242a432aehf"
    }),
    ("sha256-4242", {
        "key": "version",
        "value": "sha256-4242"
    }),
    ("sha256-4242", {
        "key": "version",
        "value": "sha256-4242"
    }),
])
def test_parse_version(version, expected):
    assert parse_version(version) == expected
