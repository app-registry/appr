from __future__ import absolute_import, division, print_function

from appr.exception import PackageReleaseNotFound, raise_channel_not_found


class ChannelBase(object):
    def __init__(self, name, package, current=None):
        self.package = package
        self.name = name
        self.current = current

    def exists(self):
        return self._exists()

    @classmethod
    def get(cls, name, package):
        raise NotImplementedError

    def current_release(self):
        return self.current

    def add_release(self, release, package_class):
        if self._check_release(release, package_class) is False:
            raise PackageReleaseNotFound("Release %s doesn't exist for package %s" %
                                         (release, self.package), {
                                             "package": self.package,
                                             "release": release})
        self.current = release
        return self.save()

    def remove_release(self, release):
        if not self.exists():
            raise_channel_not_found(self.package, self.name)
        return self._remove_release(release)

    def _check_release(self, release_name, package_class):
        release = package_class.get_release(self.package, release_name)
        if release is None or str(release) != release_name:
            return False
        else:
            return True

    def to_dict(self):
        releases = self.releases()
        return ({"releases": releases, "name": self.name, "current": self.current_release()})

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__, self.name, self.package)

    @classmethod
    def all(cls, package):
        raise NotImplementedError

    def releases(self):
        """ Returns the list of releases """
        raise NotImplementedError

    def _add_release(self, release):
        raise NotImplementedError

    def _remove_release(self, release):
        raise NotImplementedError

    def _exists(self):
        """ Check if the channel is saved already """
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    @classmethod
    def dump_all(cls, package_class=None):
        """ produce a dict with all packages """
