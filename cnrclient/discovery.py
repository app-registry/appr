import re
from html.parser import HTMLParser
import requests


package_regexp = "(.+?)/(.+)"


class MetaHTMLParser(HTMLParser):
    def __init__(self, variables):
        self.meta = {}
        self.variables = variables
        HTMLParser.__init__(self)

    def replace_values(self, s):
        for k, v in self.variables.items():
            s = s.replace("{%s}" % k, v)
        return s

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            d = dict(attrs)
            if 'name' in d and d['name'] == 'cnr-package':
                name, source = d['content'].split(" ")
                name = self.replace_values(name)
                source = self.replace_values(source)
                if name not in self.meta:
                    self.meta[name] = []
                self.meta[name].append(source)


def split_package_name(package):
    m = re.search(package_regexp, package)
    host, name = (m.group(1), m.group(2))
    return (host, name)


def ishosted(package):
    host, _ = split_package_name(package)
    if "." in host or 'localhost' in host:
        return True
    else:
        return False


def discover_sources(package, version, media_type, secure=False):
    schemes = ["https://", "http://"]
    host, name = split_package_name(package)
    for scheme in schemes:
        url = scheme + host
        try:
            r = requests.get(url, params={"cnr-discovery": 1}, timeout=2)
        except (requests.exceptions.Timeout, requests.ConnectionError) as e:
            if scheme == "https://" and not secure:
                continue
            else:
                raise e

        r.raise_for_status()
        variables = {'name': name, 'version': version,
                     "media_type": media_type,
                     "mediatype": media_type}
        p = MetaHTMLParser(variables)
        p.feed(r.content.decode())
        if package in p.meta:
            return p.meta[package]
    return None
