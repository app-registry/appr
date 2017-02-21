import os
import errno
import re


PACKAGE_REGEXP = r"^(.*?\/)?([a-z0-9_-]+\/[a-z0-9_-]+)([:@][a-z0-9._-]+|@sha256:[a-z0-9]+)?$"
# r"^(.*?)?\/?([a-z0-9_-]+\/[a-z0-9_-]+?)([:@].*)?$"


def get_media_type(mediatype):
    if mediatype:
        match = re.match(r"application/vnd\.cnr\.[a-z_-]+\.(.+?)\.(.+).(.+)", mediatype)
        if match:
            mediatype = match.group(1)
    return mediatype


def package_filename(name, version, media_type):
    return "%s_%s_%s" % (name.replace("/", "_"), version, media_type)


def parse_version(version):
    if version is None or version == "default":
        return {'key': "version", "value": "default"}
    elif str.startswith(version, "@sha256:"):
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


def split_package_name(name):
    sp = name.split("/")
    package_parts = {"host": None,
                     "namespace": None,
                     "package": None,
                     "version": None}

    if len(sp) >= 1:
        package_parts["host"] = sp[0]
    if len(sp) >= 2:
        package_parts["namespace"] = sp[1]
    if len(sp) >= 3:
        match = re.match(r"^([a-z0-9_-]+?)([:@].*)?$", sp[2])
        package, version = match.groups()
        package_parts['package'] = package
        package_parts['version'] = version
    return package_parts


def parse_package_name(name, regexp=PACKAGE_REGEXP):
    package_regexp = regexp
    match = re.match(package_regexp, name)
    if match is None:
        raise ValueError("Package '%s' does not match format '[registry/]namespace/name[@version|:channel]'" % (name))
    host, package, version = match.groups()
    if not version:
        version = 'default'
    if not host:
        host = None
    else:
        host = host[:-1]
    namespace, package = package.split("/")
    return {'host': host,
            'namespace': namespace,
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
