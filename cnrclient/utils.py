import os
import errno
import re


def package_filename(name, version, media_type):
    return "%s_%s_%s" % (name.replace("/", "_"), version, media_type)


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
