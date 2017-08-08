import os
import os.path

import yaml

from appr.config import DEFAULT_CONF_DIR
from appr.utils import mkdir_p


class ApprAuth(object):
    """ Store Auth object """

    def __init__(self, conf_directory=DEFAULT_CONF_DIR):
        self.conf_directory = conf_directory
        home = os.path.expanduser("~")
        path = "%s/%s/auths.yaml" % (home, conf_directory)
        mkdir_p(os.path.join(home, conf_directory))
        self.tokenfile = os.path.join(home, path)
        self._tokens = None
        self._retro_compat()

    def _retro_compat(self):
        new_tokens = {'auths': {}}

        if self.tokens is None:
            return

        rewrite = False
        for domain, token in self.tokens['auths'].items():
            if isinstance(token, basestring):
                new_tokens['auths'].update(self._create_token(domain, token))
                rewrite = True
            else:
                new_tokens['auths'][domain] = token
        if rewrite:
            self._write_tokens(new_tokens)
            self._tokens = new_tokens

    def _get_scope(self, scope):
        data = {'namespace': "*", 'repo': "*"}
        if scope:
            sp = scope.split("/")
            data = {'namespace': sp[0], 'repo': "*"}
            if len(sp) == 2:
                data['repo'] = sp[1]
        return data

    def _get_host(self, domain, scope):
        if scope:
            return "%s:%s" % (domain, scope)
        else:
            return domain

    def _create_token(self, domain, auth, scope=None):
        auth = {"token": auth, 'scope': self._get_scope(scope)}
        return {self._get_host(domain, scope): auth}

    @property
    def tokens(self):
        if self._tokens is None:
            if os.path.exists(self.tokenfile):
                with open(self.tokenfile, 'r') as tokenfile:
                    self._tokens = yaml.load(tokenfile.read())
            else:
                return None
        return self._tokens

    def token(self, domain, scope=None):
        if not self.tokens:
            return None

        hosts = [domain, '*']
        if scope:
            sp = scope.split("/")
            hosts = ["%s:%s" % (domain, scope), "%s:%s" % (domain, sp[0])] + hosts

        for host in hosts:
            if host in self.tokens['auths']:
                return self.tokens['auths'][host]['token']

        return None

    def add_token(self, host, value, scope=None):
        auths = self.tokens
        if auths is None:
            auths = {'auths': {}}
        auths['auths'].update(self._create_token(host, value, scope=scope))
        self._write_tokens(auths)

    def _write_tokens(self, tokens):
        with open(self.tokenfile, 'w') as tokenfile:
            tokenfile.write(
                yaml.safe_dump(tokens, indent=2, default_style='"', default_flow_style=False))

    def delete_token(self, domain, scope=None):
        host = self._get_host(domain, scope)
        auths = self.tokens

        if not auths or host not in auths['auths']:
            return None
        prev = auths['auths'].pop(host)
        self._write_tokens(auths)
        return prev
