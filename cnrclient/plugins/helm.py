import os
import subprocess

import yaml

from cnrclient.client import CnrClient
from cnrclient.utils import mkdir_p, parse_package_name
from cnrclient.pack import CnrPackage


__all__ = ['Helm']


def parse_version(version):
    if version[0] == ":" or version.startswith("channel:"):
        parts = {'key': 'channel', 'value': version.split(":")[1]}
    elif version.startswith("sha256:"):
        parts = {'key': 'digest', 'value': version.split("sha256:")[1]}
    else:
        parts = {'key': 'version', 'value': version}

    return parts


class Helm(object):
    def __init__(self):
        pass

    def download_appr_deps(self, deps, tarball=False):
        path = "dep_charts"
        mkdir_p(path)
        helm_deps = {}
        for dep in deps:
            package_parts = parse_package_name(dep['name'])
            name = package_parts['package']

            vparts = parse_version(dep['version'])
            client = CnrClient(package_parts['host'])
            package_name = "%s/%s" % (package_parts['namespace'], name)

            pullpack = client.pull_json(package_name, version_parts=vparts, media_type="helm")
            package = CnrPackage(pullpack['blob'], b64_encoded=True)
            release = pullpack['release']
            packagepath = os.path.join(path, package_parts['namespace'])
            tarpath = "%s-%s.tgz" % (name, release)
            print "Pulled package: %s (%s) \n -> %s" % (dep['name'], release, packagepath)
            if tarball:
                with open(tarpath, 'wb') as tarfile:
                    tarfile.write(package.blob)
            package.extract(packagepath)

            helm_deps[name] = {'name': name,
                               'version': release,
                               'repository': 'file://%s/%s' % (packagepath, name)}
        return helm_deps

    def build_dep(self):
        with open("requirements.yaml", "rb") as requirefile:
            deps = yaml.safe_load(requirefile.read())
        helm_deps = {}
        if "appr" in deps:
            helm_deps = self.download_appr_deps(deps['appr'])
            dict_deps = {dep['name']: dep for dep in deps['dependencies']}
            dict_deps.update(helm_deps)
            deps['dependencies'] = dict_deps.values()
            with open('requirements.yaml', "wb") as requirefile:
                requirefile.write(yaml.safe_dump(deps, default_flow_style=False))
            print "Updated requirements.yaml"

    def action(self, cmd, release, helm_opts=None):
        cmd = [cmd]
        if helm_opts:
            cmd = cmd + helm_opts
        cmd = cmd + [release]
        return self._call(cmd)

    def _call(self, cmd):
        command = ['helm'] + cmd
        try:
            return subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return e.output
