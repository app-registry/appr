import os
from flask import Flask, request
from flask_cors import CORS


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
        app.config.from_object('cnr.api.config.DevelopmentConfig')
    else:
        app.config.from_object('cnr.api.config.ProductionConfig')
    from cnr.api.info import info_app
    from cnr.api.registry import registry_app
    app.register_blueprint(info_app, url_prefix='/cnr')
    app.register_blueprint(registry_app, url_prefix='/cnr')
    app.logger.info("Start service")
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host='0.0.0.0')
