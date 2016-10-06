import cnr.semver as semver
from cnr.exception import PackageVersionNotFound, raise_channel_not_found


class ChannelBase(object):
    def __init__(self, name, package):
        self.package = package
        self.name = name
        self._iscreated = None
        self.current = None

    def exists(self):
        return self._exists()

    def current_release(self, releases=None):
        if self.current:
            return self.current

        if releases is None:
            releases = self.releases()
        if not releases:
            return None
        ordered_versions = [str(x) for x in sorted(semver.versions(releases, False),
                                                   reverse=True)]
        return ordered_versions[0]

    def add_release(self, version, package_class):
        if self._check_release(version, package_class) is False:
            raise PackageVersionNotFound("Release %s doesn't exist for package %s" % (version, self.package),
                                         {"package": self.package, "version": version})
        if not self.exists():
            self.save()
        return self._add_release(version)

    def remove_release(self, version):
        if not self.exists():
            raise_channel_not_found(self.package, self.name)
        return self._remove_release(version)

    def _check_release(self, release_name, package_class):
        version = package_class.get_version(self.package, release_name)
        if version is None or str(version) != release_name:
            return False
        else:
            return True

    def to_dict(self):
        releases = self.releases()
        return ({"releases": releases,
                 "name": self.name,
                 "current": self.current_release(releases)})

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__, self.name, self.package)

    @classmethod
    def all(cls, package):
        raise NotImplementedError

    def releases(self):
        """ Returns the list of versions """
        raise NotImplementedError

    def _add_release(self, version):
        # etcdctl put /{self.package/channels/{self.name}/version
        raise NotImplementedError

    def _remove_release(self, version):
        # etcdctl put /{self.package/channels/{self.name}/version
        raise NotImplementedError

    def _exists(self):
        """ Check if the channel is saved already """
        raise NotImplementedError

    def save(self, force=False):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    @classmethod
    def dump_all(cls, package_class=None):
        """ produce a dict with all packages """
