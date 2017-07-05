from __future__ import absolute_import, division, print_function

import os
import os.path

import yaml

from appr.utils import mkdir_p

DEFAULT_CONF_DIR = os.getenv('APPR_CONF_DIR', ".appr")


class ApprConfig(object):
    """ Store Auth object """

    def __init__(self, conf_directory=DEFAULT_CONF_DIR):
        self.conf_directory = conf_directory
        home = os.path.expanduser("~")
        mkdir_p(os.path.join(home, conf_directory))
        path = "%s/%s/config.yaml" % (home, conf_directory)
        self.configfile = os.path.join(home, path)
        self._config = None

    @property
    def config(self):
        if self._config is None:
            if os.path.exists(self.configfile):
                with open(self.configfile, 'r') as configfile:
                    self._config = yaml.load(configfile.read())
            else:
                self._config = {}
        return self._config

    def add_key(self, key, value):
        self.config[key] = value
        self._write_config(self.config)

    def _write_config(self, config):
        with open(self.configfile, 'w') as configfile:
            configfile.write(
                yaml.safe_dump(config, indent=2, default_style='"', default_flow_style=False))

    def add_registry_alias(self, alias, target):
        if 'repositories' not in self.config:
            self.config['repositories'] = {}
        self.config['repositories'][alias] = target
        self._write_config(self.config)

    def get_registry_alias(self, alias):
        if 'repositories' in self.config:
            return self.config['repositories'].get(alias, None)
        return None
