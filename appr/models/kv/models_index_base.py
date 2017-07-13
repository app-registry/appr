from __future__ import absolute_import, division, print_function

import datetime
import json

import appr.semver
from appr.exception import (PackageAlreadyExists, PackageNotFound, ResourceNotFound,
                            raise_channel_not_found, raise_package_not_found)

DEFAULT_LOCK_TIMEOUT = 3


class ModelsIndexBase(object):
    packages_key = "packages.json"

    def __init__(self, package=None):
        self._packages = None
        self._releases = None
        self.package = package
        self.locks = set()

    @property
    def releases_key(self):
        return self.package + "/" + "releases.json"

    @property
    def releases_data(self):
        path = self.releases_key
        if self._releases is None:
            try:
                self._releases = self._fetch_data(path)
            except ResourceNotFound:
                raise_package_not_found(self.package)
        return self._releases

    def blob_key(self, digest, mod="sha256"):
        return "%s/digests/%s/%s" % (self.package, mod, digest)

    def add_blob(self, b64blob, digest):
        try:
            path = self.blob_key(digest)
            self.get_lock(path)
            self._write_raw_data(path, b64blob)
            return True
        finally:
            self.release_lock(path)

    def delete_blob(self, digest):
        try:
            path = self.blob_key(digest)
            self.get_lock(path)
            self._delete_data(path)
            return True
        finally:
            self.release_lock(path)

    def get_blob(self, digest):
        try:
            path = self.blob_key(digest)
            return self._fetch_raw_data(path)
        except ResourceNotFound:
            raise_package_not_found(self.package, digest)

    def add_package(self, package_name):
        try:
            self.get_lock(self.packages_key)
            namespace, name = package_name.split("/")
            if namespace not in self.packages_data['packages']:
                self.packages_data['packages'][namespace] = {}
            if name not in self.packages_data['packages'][namespace]:
                pdata = {
                    "created_at": datetime.datetime.utcnow().isoformat(),
                    'name': name,
                    'namespace': namespace}
                self.packages_data['packages'][namespace][name] = pdata
                self._write_data(self.packages_key, self.packages_data)
        finally:
            self.release_lock(self.packages_key)

    def delete_package(self, package_name):
        try:
            self.get_lock(self.packages_key)
            namespace, name = package_name.split("/")
            if (namespace not in self.packages_data['packages'] or
                    name not in self.packages_data['packages'][namespace]):
                return None
            pdata = self.packages_data['packages'][namespace].pop(name)
            if not self.packages_data['packages'][namespace]:
                self.packages_data['packages'].pop(namespace)
            self._write_data(self.packages_key, self.packages_data)
            return pdata
        finally:
            self.release_lock(self.packages_key)

    def add_release(self, package_data, release, media_type, force=False):
        try:
            self.get_lock(self.releases_key)
            try:
                data = self.releases_data
            except PackageNotFound:
                data = {'page': 0, 'channels': {}, 'releases': {}}
            if release not in data['releases']:
                data['releases'][release] = {'manifests': {}, 'channels': []}

            if (release in data['releases'] and
                    media_type in data['releases'][release]['manifests'] and not force):
                raise PackageAlreadyExists("Package exists already", {
                    "package": self.package,
                    "release": release,
                    "media_type": media_type})
            data['releases'][release]['manifests'][media_type] = package_data
            self._write_data(self.releases_key, data)
            self.add_package(self.package)
            return data
        finally:
            self.release_lock(self.releases_key)

    def delete_release(self, release, media_type):
        try:
            self.get_lock(self.releases_key)
            data = self.releases_data
            if release not in data['releases'] or media_type not in data['releases'][release][
                    'manifests']:
                raise_package_not_found(self.package)
            data['releases'][release]['manifests'].pop(media_type)
            if not data['releases'][release]['manifests']:
                data['releases'].pop(release)
            if not data['releases']:
                self.delete_package(self.package)
            self._write_data(self.releases_key, data)
            return True
        finally:
            self.release_lock(self.releases_key)

    @property
    def packages_data(self):
        if self._packages is None:
            try:
                self._packages = self._fetch_data(self.packages_key)
            except ResourceNotFound:
                try:
                    self.get_lock(self.packages_key, timeout=None)
                    self._packages = {"page": 0, "packages": {}}
                    self._write_data(self.packages_key, self._packages)
                finally:
                    self.release_lock(self.packages_key)

        return self._packages

    def releases(self, media_type=None):
        if media_type is not None:
            result = []
            for release_name, release in self.releases_data['releases'].iteritems():
                if media_type in release['manifests']:
                    result.append(release_name)
        else:
            result = self.releases_data['releases'].keys()
        return result

    def release_manifests(self, release):
        try:
            manifests = self.releases_data['releases'][release]['manifests']
            return manifests
        except KeyError:
            raise_package_not_found(self.package, release)

    def release_formats(self, release=None):
        if release:
            return self.release_manifests(release).keys()
        else:
            formats = set()
            for _, release in self.releases_data['releases'].iteritems():
                [formats.add(x) for x in release['manifests'].keys()]
            return list(formats)

    def release(self, release, media_type):
        try:
            return self.release_manifests(release)[media_type]
        except KeyError:
            raise_package_not_found(self.package, release, media_type)

    def ispackage_exists(self):
        return (len(self.releases()) > 0)

    def channels(self):
        data = self.releases_data['channels']
        if data:
            return data.values()
        else:
            return []

    def channel(self, channel):
        try:
            return self.releases_data['channels'][channel]
        except KeyError:
            raise_channel_not_found(channel)

    def _set_channel(self, channel, release):
        try:
            self.get_lock(self.releases_key)
            data = self.releases_data
            data['channels'][channel] = {
                'name': channel,
                'current': release,
                'package': self.package}
            if channel not in data['releases'][release]['channels']:
                data['releases'][release]['channels'].append(channel)
            self._write_data(self.releases_key, data)
            return True
        finally:
            self.release_lock(self.releases_key)

    def add_channel(self, channel, current):
        return self._set_channel(channel, current)

    def delete_channel(self, channel):
        """ Delete the channel from all releases """
        if not self.ischannel_exists(channel):
            raise_channel_not_found(channel)
        try:
            self.get_lock(self.releases_key)
            data = self.releases_data
            for release in self.channel_releases(channel):
                self._releases = self._delete_channel_release(channel, release)
            if channel in data['channels']:
                data['channels'].pop(channel)
            self._write_data(self.releases_key, data)
        finally:
            self.release_lock(self.releases_key)

    def set_channel_default(self, channel, release):
        self._check_channel_release(channel, release)
        return self._set_channel(channel, release)

    def _check_channel_release(self, channel, release):
        if not self.ischannel_exists(channel):
            raise_channel_not_found(channel)
        if release not in self.releases_data['releases']:
            raise_package_not_found(self.package, release)

    def add_channel_release(self, channel, release):
        self._check_channel_release(channel, release)
        try:
            self.get_lock(self.releases_key)
            data = self.releases_data
            if channel not in data['releases'][release]['channels']:
                data['releases'][release]['channels'].append(channel)
            self._write_data(self.releases_key, data)
            return True
        finally:
            self.release_lock(self.releases_key)

    def delete_channel_release(self, channel, release):
        self._check_channel_release(channel, release)
        try:
            self.get_lock(self.releases_key)
            data = self._delete_channel_release(channel, release)
            releases = self.channel_releases(channel)
            if not releases:
                data['channels'].pop(channel)
            else:
                self.set_channel_default(channel, releases[0])
            self._write_data(self.releases_key, data)
            return True
        finally:
            self.release_lock(self.releases_key)

    def _delete_channel_release(self, channel, release):
        data = self.releases_data
        channels = set(data['releases'][release]['channels'])
        if channel in channels:
            channels.discard(channel)
            data['releases'][release]['channels'] = list(channels)
        return data

    def channel_releases(self, channel):
        if not self.ischannel_exists(channel):
            raise_channel_not_found(self.package, channel)

        releases = [
            release for release, x in self.releases_data['releases'].iteritems()
            if channel in x['channels']]
        ordered_releases = [
            str(x) for x in sorted(appr.semver.versions(releases, False), reverse=True)]
        return ordered_releases

    def release_channels(self, release):
        if release not in self.releases_data['releases']:
            raise_package_not_found(self.package, release)
        return self.releases_data['releases'][release]['channels']

    def package_names(self, namespace=None):
        result = []
        if namespace is not None:
            if namespace in self.packages_data['packages']:
                result = [
                    "%s/%s" % (namespace, name)
                    for name in self.packages_data['packages'][namespace].keys()]
        else:
            for namespace, packages in self.packages_data['packages'].iteritems():
                for name in packages.keys():
                    result.append("%s/%s" % (namespace, name))
        return result

    def ischannel_exists(self, channel):
        return channel in self.releases_data['channels']

    def packages(self, namespace=None):
        result = []
        if namespace is not None:
            if namespace in self.packages_data['packages']:
                result = self.packages_data['packages'][namespace].values()
        else:
            for namespace, packages in self.packages_data['packages'].iteritems():
                for _, data in packages.iteritems():
                    result.append(data)
        return result

    def _lock_key(self, key):
        return "%s.lock" % (key)

    def get_lock(self, key, ttl=3, timeout=DEFAULT_LOCK_TIMEOUT):
        lock_key = self._lock_key(key)
        if lock_key not in self.locks:
            self._get_lock(lock_key, ttl, timeout)
            self.locks.add(lock_key)

    def release_lock(self, key):
        """ Check if owner of the lock """
        lock_key = self._lock_key(key)
        if lock_key in self.locks:
            self.locks.discard(lock_key)
            self._release_lock(lock_key)

    def _get_lock(self, key, ttl=3, timeout=DEFAULT_LOCK_TIMEOUT):
        raise NotImplementedError

    def _release_lock(self, key):
        """ Remove the lock """
        raise NotImplementedError

    def _fetch_data(self, key):
        return json.loads(self._fetch_raw_data(key))

    def _fetch_raw_data(self, key):
        raise NotImplementedError

    def _write_data(self, key, data):
        return self._write_raw_data(key, json.dumps(data))

    def _write_raw_data(self, key, data):
        raise NotImplementedError

    def _delete_data(self, key):
        raise NotImplementedError
