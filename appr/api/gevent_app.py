#!/usr/bin/env python
import os

from gevent.pywsgi import WSGIServer

from appr.api.app import create_app

class GeventApp(object):
    def __init__(self, options=None):
        self.args_options = options or {}
        os.environ['APPR_DB_CLASS'] = self.args_options.db_class
        print("Listening %s:%s" % (self.args_options.bind, self.args_options.port))
        self.http_server = WSGIServer((self.args_options.bind, self.args_options.port),
                                      create_app())

    def run(self):
        self.http_server.serve_forever()
