import os
import errno
import re


def get_media_type(mediatype):
    if mediatype:
        match = re.match(r"application/vnd\.cnr\.[a-z_-]+\.(.+?)\.(.+).(.+)", mediatype)
        if match:
            mediatype = match.group(1)
    return mediatype


def package_filename(name, version, media_type):
    return "%s_%s_%s" % (name.replace("/", "_"), version, media_type)


def parse_version(version):
    if str.startswith(version, "@sha256:"):
        return {'key': 'digest',
                'value': version.split("@sha256:")[1]}
    elif version[0] == "@":
        return {'key': 'version',
                'value': version[1:]}
    elif version[0] == ":":
        return {'key': 'channel',
                'value': version[1:]}
    else:
        return {'key': 'unknown', 'value': version}


def parse_package_name(name):
    package_regexp = r"^(.*?)?\/?([a-z0-9_-]+\/[a-z0-9_-]+?)([:@].*)?$"
    match = re.match(package_regexp, name)
    if match is None:
        raise ValueError("Package '%s' does not match format '[registry/]namespace/name[@version|:channel]'" % (name))
    host, package, version = match.groups()
    if not version:
        version = 'default'
    if not host:
        host = None
    return {'host': host,
            'package': package,
            'version': version}


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
