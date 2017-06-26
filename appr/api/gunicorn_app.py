#!/usr/bin/env python
import gunicorn.app.base
from gunicorn.six import iteritems

from appr.api.wsgi import app


class GunicornApp(gunicorn.app.base.BaseApplication):
    def __init__(self, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__(options)

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(vars(self.options))
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
