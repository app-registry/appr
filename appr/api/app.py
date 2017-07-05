from __future__ import absolute_import, division, print_function

import os

from flask import Flask, request
from flask_cors import CORS

from appr.api.config import DevelopmentConfig, ProductionConfig
from appr.exception import InvalidUsage


def getvalues():
    jsonbody = request.get_json(force=True, silent=True)
    values = request.values.to_dict()
    if jsonbody:
        values.update(jsonbody)
    return values


def create_app():
    app = Flask(__name__)
    CORS(app)
    setting = os.getenv('APP_ENV', "development")
    if setting != 'production':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)
    from appr.api.info import info_app
    from appr.api.registry import registry_app
    app.register_blueprint(info_app, url_prefix='/cnr')
    app.register_blueprint(registry_app, url_prefix='/cnr')
    app.logger.info("Start service")
    return app


def repo_name(namespace, name):
    def _check(name, scope):
        if name is None:
            raise InvalidUsage("%s: %s is malformed" % (scope, name), {'name': name})

    _check(namespace, 'namespace')
    _check(name, 'package-name')
    return "%s/%s" % (namespace, name)


if __name__ == "__main__":
    application = create_app()
    application.run(host='0.0.0.0')
