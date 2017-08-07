from __future__ import absolute_import, division, print_function

import json
from base64 import b64decode

from flask import Blueprint, current_app, jsonify, request

import appr.api.impl.registry
from appr.api.app import getvalues, repo_name
from appr.exception import (
    ApprException, ChannelNotFound, InvalidParams, InvalidRelease, InvalidUsage,
    PackageAlreadyExists, PackageNotFound, PackageReleaseNotFound, UnableToLockResource,
    UnauthorizedAccess, Unsupported)
from appr.models import DEFAULT_MEDIA_TYPE, Blob, Channel, Package

registry_app = Blueprint(
    'registry',
    __name__, )


@registry_app.errorhandler(Unsupported)
@registry_app.errorhandler(PackageAlreadyExists)
@registry_app.errorhandler(InvalidRelease)
@registry_app.errorhandler(UnableToLockResource)
@registry_app.errorhandler(UnauthorizedAccess)
@registry_app.errorhandler(PackageNotFound)
@registry_app.errorhandler(PackageReleaseNotFound)
@registry_app.errorhandler(ApprException)
@registry_app.errorhandler(InvalidUsage)
@registry_app.errorhandler(InvalidParams)
@registry_app.errorhandler(ChannelNotFound)
def render_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@registry_app.before_request
def pre_request_logging():
    jsonbody = request.get_json(force=True, silent=True)
    values = request.values.to_dict()
    if jsonbody:
        values.update(jsonbody)

    current_app.logger.info("request", extra={
        "remote_addr": request.remote_addr,
        "http_method": request.method,
        "original_url": request.url,
        "path": request.path,
        "data": values,
        "headers": dict(request.headers.to_list())})


@registry_app.route("/test_error")
def test_error():
    raise InvalidUsage("error message", {"path": request.path})


def _pull(data, json_format=True):
    if json_format:
        resp = jsonify(data)
    else:
        resp = current_app.make_response(b64decode(data['blob']))
        resp.headers['Content-Disposition'] = data['filename']
        resp.mimetype = 'application/x-gzip'
    return resp


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/blobs/sha256/<string:digest>",
    methods=['GET'], strict_slashes=False)
def blobs(namespace, package_name, digest):
    reponame = repo_name(namespace, package_name)
    data = appr.api.impl.registry.pull_blob(reponame, digest, blob_class=Blob)
    json_format = request.args.get('format', None) == 'json'
    return _pull(data, json_format=json_format)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/blobs/sha256/<string:digest>/json",
    methods=['GET'], strict_slashes=False)
def blobs_json(namespace, package_name, digest):
    reponame = repo_name(namespace, package_name)
    data = appr.api.impl.registry.pull_blob(reponame, digest, blob_class=Blob)
    return _pull(data, json_format=True)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>/<string:media_type>/pull",
    methods=['GET'], strict_slashes=False)
def pull(namespace, package_name, release, media_type):
    reponame = repo_name(namespace, package_name)
    data = appr.api.impl.registry.pull(reponame, release, media_type, Package, blob_class=Blob)
    json_format = request.args.get('format', None) == 'json'
    return _pull(data, json_format=json_format)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>/<string:media_type>/pull/json",
    methods=['GET'], strict_slashes=False)
def pull_json(namespace, package_name, release, media_type):
    reponame = repo_name(namespace, package_name)
    data = appr.api.impl.registry.pull(reponame, release, media_type, Package, blob_class=Blob)
    return _pull(data, json_format=True)


@registry_app.route("/api/v1/packages/<string:namespace>/<string:package_name>", methods=['POST'],
                    strict_slashes=False)
def push(namespace, package_name):
    reponame = repo_name(namespace, package_name)
    values = getvalues()
    release = values['release']
    media_type = values.get('media_type', DEFAULT_MEDIA_TYPE)
    force = (values.get('force', 'false') == 'true')
    metadata = values.get('metadata', None)
    blob = Blob(reponame, values['blob'])
    result = appr.api.impl.registry.push(reponame, release, media_type, blob, force, Package,
                                         metadata=metadata)
    return jsonify(result)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>/<string:media_type>",
    methods=['DELETE'], strict_slashes=False)
def delete_package(namespace, package_name, release, media_type):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.delete_package(reponame, release, media_type,
                                                   package_class=Package)
    return jsonify(result)


@registry_app.route("/api/v1/packages", methods=['GET'], strict_slashes=False)
def list_packages():
    values = getvalues()
    namespace = values.get('namespace', None)
    result = appr.api.impl.registry.list_packages(namespace, Package, search=values.get(
        'query', None), media_type=values.get('media_type', None))
    resp = current_app.make_response(json.dumps(result))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route("/api/v1/packages/search", methods=['GET'], strict_slashes=False)
def search_packages():
    values = getvalues()
    query = values.get("q")
    result = appr.api.impl.registry.search(query, Package)
    return jsonify(result)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>/<string:media_type>",
    methods=['GET'], strict_slashes=False)
def show_package(namespace, package_name, release, media_type):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.show_package(reponame, release, media_type,
                                                 channel_class=Channel, package_class=Package)
    return jsonify(result)


@registry_app.route("/api/v1/packages/<string:namespace>/<string:package_name>", methods=['GET'],
                    strict_slashes=False)
def show_package_releases(namespace, package_name):
    reponame = repo_name(namespace, package_name)
    media_type = getvalues().get('media_type', None)
    result = appr.api.impl.registry.show_package_releases(reponame, media_type=media_type,
                                                          package_class=Package)
    return jsonify(result)


@registry_app.route("/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>",
                    methods=['GET'], strict_slashes=False)
def show_package_release_manifests(namespace, package_name, release):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.show_package_manifests(reponame, release,
                                                           package_class=Package)
    return jsonify(result)


# CHANNELS
@registry_app.route("/api/v1/packages/<string:namespace>/<string:package_name>/channels", methods=[
    'GET'], strict_slashes=False)
def list_channels(namespace, package_name):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.list_channels(reponame, Channel)
    resp = current_app.make_response(json.dumps(result))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/channels/<string:channel_name>",
    methods=['GET'], strict_slashes=False)
def show_channel(namespace, package_name, channel_name):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.show_channel(reponame, channel_name, Channel)
    return jsonify(result)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/channels/<string:channel_name>/<string:release>",
    methods=['POST'], strict_slashes=False)
def add_channel_release(namespace, package_name, channel_name, release):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.add_channel_release(
        reponame, channel_name, release, channel_class=Channel, package_class=Package)
    return jsonify(result)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/channels/<string:channel_name>/<string:release>",
    methods=['DELETE'], strict_slashes=False)
def delete_channel_release(namespace, package_name, channel_name, release):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.delete_channel_release(
        reponame, channel_name, release, channel_class=Channel, package_class=Package)
    return jsonify(result)


@registry_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/channels/<string:channel_name>",
    methods=['DELETE'], strict_slashes=False)
def delete_channel(namespace, package_name, channel_name):
    reponame = repo_name(namespace, package_name)
    result = appr.api.impl.registry.delete_channel(reponame, channel_name, channel_class=Channel)
    return jsonify(result)
