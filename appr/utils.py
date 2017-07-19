from __future__ import absolute_import, division, print_function

import collections
import errno
import importlib
import os
import os.path
import re
import sys
import itertools
from termcolor import colored

PACKAGE_REGEXP = r"^(.*?\/)([a-z0-9_-]+\/[a-z0-9_-]+)([:@][a-z0-9._+-]+|@sha256:[a-z0-9]+)?$"


def get_media_type(mediatype):
    if mediatype:
        match = re.match(r"application/vnd\.appr\.[a-z_-]+\.(.+?)\.(.+).(.+)", mediatype)
        if match:
            mediatype = match.group(1)
    return mediatype


def package_filename(name, version, media_type):
    return "%s_%s_%s" % (name.replace("/", "_"), version, media_type)


def parse_version(version):
    if version is None or version == "default":
        return {'key': "version", "value": "default"}
    elif str.startswith(version, "@sha256:"):
        return {'key': 'digest', 'value': version.split("@sha256:")[1]}
    elif version[0] == "@":
        return {'key': 'version', 'value': version[1:]}
    elif version[0] == ":":
        return {'key': 'channel', 'value': version[1:]}
    else:
        return {'key': 'unknown', 'value': version}


def parse_version_req(version):
    """
     Converts a version string to a dict with following rules:
       if string starts with ':' it is a channel
       if string starts with 'sha256' it is a digest
       else it is a release
    """
    if version is None:
        version = "default"
    if version[0] == ':' or version.startswith('channel:'):
        parts = {'key': 'channel', 'value': version.split(':')[1]}
    elif version.startswith('sha256:'):
        parts = {'key': 'digest', 'value': version.split('sha256:')[1]}
    else:
        parts = {'key': 'version', 'value': version}
    return parts


def split_package_name(name):
    sp = name.split("/")
    package_parts = {"host": None, "namespace": None, "package": None, "version": None}

    if len(sp) >= 1:
        package_parts["host"] = sp[0]
    if len(sp) >= 2:
        package_parts["namespace"] = sp[1]
    if len(sp) >= 3:
        match = re.match(r"^([a-z0-9_-]+?)([:@][a-z0-9._+-]+|@sha256:[a-z0-9]+)?$", sp[2])
        package, version = match.groups()
        package_parts['package'] = package
        package_parts['version'] = version
    return package_parts


def parse_package_name(name, regexp=PACKAGE_REGEXP):
    package_regexp = regexp
    match = re.match(package_regexp, name)
    if match is None:
        raise ValueError(
            "Package '%s' does not match format 'registry/namespace/name[@version|:channel]'" %
            (name))
    host, package, version = match.groups()
    if not version:
        version = 'default'
    if not host:
        host = None
    else:
        host = host[:-1]
    namespace, package = package.split("/")
    return {'host': host, 'namespace': namespace, 'package': package, 'version': version}


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def colorize(status):
    msg = {}
    if os.getenv("APPR_COLORIZE_OUTPUT", "true") == "true":
        msg = {
            'ok': 'green',
            'created': 'yellow',
            'updated': 'cyan',
            'replaced': 'yellow',
            'absent': 'green',
            'deleted': 'red',
            'protected': 'magenta'}
    color = msg.get(status, None)
    if color:
        return colored(status, color)
    else:
        return status


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def convert_utf8(data):
    try:
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(convert_utf8, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert_utf8, data))
        else:
            return data
    except UnicodeEncodeError as exc:
        return data

# from celery/kombu https://github.com/celery/celery (BSD license)
def symbol_by_name(name, aliases={}, imp=None, package=None, sep='.', default=None, **kwargs):
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        celery.concurrency.processes.TaskPool
                                    ^- class name

    or using ':' to separate module and symbol::

        celery.concurrency.processes:TaskPool

    If `aliases` is provided, a dict containing short name/long name
    mappings, the name is looked up in the aliases first.

    Examples:

        >>> symbol_by_name('celery.concurrency.processes.TaskPool')
        <class 'celery.concurrency.processes.TaskPool'>

        >>> symbol_by_name('default', {
        ...     'default': 'celery.concurrency.processes.TaskPool'})
        <class 'celery.concurrency.processes.TaskPool'>

        # Does not try to look up non-string names.
        >>> from celery.concurrency.processes import TaskPool
        >>> symbol_by_name(TaskPool) is TaskPool
        True

    """

    def _reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    if imp is None:
        imp = importlib.import_module

    if not isinstance(name, basestring):
        return name  # already a class

    name = aliases.get(name) or name
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        try:
            module = imp(module_name, package=package, **kwargs)
        except ValueError as exc:
            _reraise(ValueError,
                     ValueError("Couldn't import {0!r}: {1}".format(name, exc)), sys.exc_info()[2])
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default


def get_current_script_path():
    executable = sys.executable
    if os.path.basename(executable) == "appr":
        path = executable
    else:
        path = sys.argv[0]
    return os.path.realpath(path)


def flatten(array):
    return list(itertools.chain(*array))
