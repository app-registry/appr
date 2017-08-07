#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import gunicorn.app.base
from gunicorn.six import iteritems

from appr.api.app import create_app


class GunicornApp(gunicorn.app.base.BaseApplication):
    def __init__(self, options=None):
        self.args_options = options or {}
        self.application = create_app()
        self.defaults = {}
        # {"worker_class": "gunicorn.workers.gthread.ThreadWorker"}

        super(GunicornApp, self).__init__(self.args_options)

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(vars(self.args_options))
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(self.defaults):
            config[key] = value
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
