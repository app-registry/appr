import json
from base64 import b64decode
from flask import jsonify, request, Blueprint, current_app
from cnr.api.app import getvalues
import cnr.api.impl.registry
from cnr.exception import (CnrException,
                           InvalidUsage,
                           InvalidVersion,
                           PackageAlreadyExists,
                           ChannelAlreadyExists,
                           PackageNotFound,
                           ChannelNotFound,
                           PackageVersionNotFound)

# @TODO chose data model from configuration
from cnr.models.etcd.package import Package
from cnr.models.etcd.channel import Channel


registry_app = Blueprint('registry', __name__,)


@registry_app.errorhandler(PackageAlreadyExists)
@registry_app.errorhandler(ChannelAlreadyExists)
@registry_app.errorhandler(InvalidVersion)
@registry_app.errorhandler(PackageNotFound)
@registry_app.errorhandler(PackageVersionNotFound)
@registry_app.errorhandler(CnrException)
@registry_app.errorhandler(InvalidUsage)
@registry_app.errorhandler(ChannelNotFound)
def render_error(error):
    response = jsonify({"error": error.to_dict()})
    response.status_code = error.status_code
    return response


@registry_app.route("/test_error")
def test_error():
    raise InvalidUsage("error message", {"path": request.path})


@registry_app.route("/api/v1/packages/<path:package>/pull", methods=['GET'], strict_slashes=False)
def pull(package):
    values = getvalues()
    version = values.get("version", None)
    data = cnr.api.impl.registry.pull(package, version, Package)
    if 'format' in values and values['format'] == 'json':
        resp = jsonify({"package": data['package'], "blob": data['blob']})
    else:
        resp = current_app.make_response(b64decode(data['blob']))
        resp.headers['Content-Disposition'] = data['filename']
        resp.mimetype = 'application/x-gzip'
    return resp


@registry_app.route("/api/v1/packages", methods=['POST'], strict_slashes=False)
def push():
    values = getvalues()
    blob = values['blob']
    package = values['package']
    version = values['version']
    force = False
    if 'force' in values:
        force = 'true' == values['force']

    r = cnr.api.impl.registry.push(package, version, blob, force, Package)
    return jsonify(r)


@registry_app.route("/api/v1/packages", methods=['GET'], strict_slashes=False)
def list_packages():
    values = getvalues()
    namespace = values.get('namespace', None)
    r = cnr.api.impl.registry.list_packages(namespace, Package)
    resp = current_app.make_response(json.dumps(r))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route("/api/v1/packages/search", methods=['GET'], strict_slashes=False)
def search_packages():
    values = getvalues()
    query = values.get("q")
    r = cnr.api.impl.registry.search(query, Package)
    return jsonify(r)


@registry_app.route("/api/v1/packages/search_reindex", methods=['POST'], strict_slashes=False)
def search_reindex():
    r = cnr.api.impl.registry.search_reindex(Package)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>", methods=['GET'], strict_slashes=False)
def show_package(package):
    values = getvalues()
    version = values.get("version", 'default')
    r = cnr.api.impl.registry.show_package(package, version,
                                           channel_class=Channel,
                                           package_class=Package)
    return jsonify(r)


# CHANNELS
@registry_app.route("/api/v1/packages/<path:package>/channels", methods=['GET'], strict_slashes=False)
def list_channels(package):
    r = cnr.api.impl.registry.list_channels(package, Channel)
    resp = current_app.make_response(json.dumps(r))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>", methods=['GET'], strict_slashes=False)
def show_channel(package, name):
    r = cnr.api.impl.registry.show_channel(package, name, Channel)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>/<string:release>",
                    methods=['POST'], strict_slashes=False)
def add_channel_release(package, name, release):
    r = cnr.api.impl.registry.add_channel_release(package, name, release,
                                                  channel_class=Channel,
                                                  package_class=Package)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>/<string:release>",
                    methods=['DELETE'], strict_slashes=False)
def delete_channel_release(package, name, release):
    r = cnr.api.impl.registry.delete_channel_release(package, name, release,
                                                     channel_class=Channel,
                                                     package_class=Package)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>",
                    methods=['POST'], strict_slashes=False)
def create_channel(package, name):
    r = cnr.api.impl.registry.create_channel(package, name, Channel)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>",
                    methods=['DELETE'], strict_slashes=False)
def delete_channel(package, name):
    r = cnr.api.impl.registry.delete_channel(package, name,
                                             channel_class=Channel)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<string:namespace>/<string:name>", methods=['DELETE'], strict_slashes=False)
def delete_package(namespace, name):
    package = "%s/%s" % (namespace, name)
    values = getvalues()
    version = values.get("version", "default")
    r = cnr.api.impl.registry.delete_package(package, version,
                                             package_class=Package,
                                             channel_class=Channel)
    return jsonify(r)
