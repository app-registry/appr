import re
import datetime
import semantic_version
from cnr.semver import last_version, select_version
from cnr.exception import (InvalidRelease,
                           PackageAlreadyExists,
                           raise_package_not_found,
                           PackageReleaseNotFound)
from cnr.models import DEFAULT_MEDIA_TYPE
from cnr.models.blob_base import BlobBase

SCHEMA_VERSION = "v1"


class PackageBase(object):
    def __init__(self, package_name, release=None,
                 media_type=DEFAULT_MEDIA_TYPE, blob=None):
        self.package = package_name
        self.media_type = media_type
        self.namespace, self.name = package_name.split("/")
        self.release = release
        self._data = None
        self.created_at = None
        self.packager = None
        self._blob = None
        self._blob_size = 0
        self._digest = None
        self._blob = None
        self.blob = blob

    @property
    def blob(self):
        return self._blob

    @blob.setter
    def blob(self, value):
        if value is not None:
            if not isinstance(value, BlobBase):
                raise ValueError("blob must be a BlobBase instance")
        self._blob = value

    def channels(self, channel_class):
        """ Returns all available channels for a package """
        channels = channel_class.all(self.package)
        result = []
        for channel in channels:
            releases = channel.releases()
            if self.release in releases:
                result.append(channel)
        return result

    @property
    def digest(self):
        if not self._digest and self.blob:
            self._digest = self.blob.digest
        return self._digest

    @property
    def blob_size(self):
        if not self._blob_size and self.blob:
            self._blob_size = self.blob.size
        return self._blob_size

    @property
    def content_media_type(self):
        return "application/vnd.cnr.package.%s.%s.tar+gzip" % (self.media_type, SCHEMA_VERSION)

    @property
    def manifest_media_type(self):
        return "application/vnd.cnr.package-manifest.%s.%s.json" % (self.media_type, SCHEMA_VERSION)

    def set_media_type(self, mediatype):
        self.media_type = re.match(r"application/vnd\.cnr\.package-manifest\.(.+?)\.(.+).json", mediatype).group(1)

    def content_descriptor(self):
        return {"mediaType": self.content_media_type,
                "size": self.blob_size,
                "digest": self.digest,
                "urls": []}

    @classmethod
    def view_manifests(cls, package, release):
        view = {'name': package}
        view['release'] = release
        view['manifests'] = cls.manifests(package, release)
        return view

    @classmethod
    def view_releases(cls, package):
        result = []
        for release in cls.all_releases(package):
            result.append(cls.view_manifests(package, release))
        return result

    @property
    def data(self):
        if self._data is None:
            self._data = {'created_at': datetime.datetime.utcnow().isoformat()}
        d = {"package": self.package,
             "release": self.release,
             "mediaType": self.manifest_media_type,
             "content": self.content_descriptor()}
        self._data.update(d)
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self.created_at = data['created_at']
        self.release = data['release']
        self._digest = data['content']['digest']
        self._blob_size = data['content']['size']
        self.set_media_type(data['mediaType'])

    @classmethod
    def check_release(cls, release):
        try:
            semantic_version.Version(release)
        except ValueError as e:
            raise InvalidRelease(e.message, {"version": release})
        return None

    @classmethod
    def get(cls, package, release='default', media_type=DEFAULT_MEDIA_TYPE):
        """
        package: string following "namespace/package_name" format
        release: release query. If None return latest release

        returns: (package blob(targz) encoded in base64, release)
        """
        p = cls(package, release)
        p.pull(release, media_type)
        return p

    @classmethod
    def get_release(cls, package, release_query, stable=False):
        releases = cls.all_releases(package)
        if not releases:
            raise_package_not_found(package, release=release_query)
        if release_query is None or release_query == 'default':
            return last_version(releases, stable)
        else:
            try:
                return select_version(releases, str(release_query), stable)
            except ValueError as e:
                raise InvalidRelease(e.message, {"release": release_query})

    def pull(self, release_query=None, media_type=DEFAULT_MEDIA_TYPE):
        if release_query is None:
            release_query = self.release
        package = self.package
        release = self.get_release(package, release_query)
        if release is None:
            raise PackageReleaseNotFound("No release match '%s' for package '%s'" % (release_query, package),
                                         {"package": package, "release_query": release_query})

        self.data = self._fetch(package, str(release), media_type)
        return self

    def save(self, force=False):
        self.check_release(self.release)
        if self.isdeleted_release(self.package, self.release) and not force:
            raise PackageAlreadyExists("Package release %s existed" % self.package,
                                       {"package": self.package, "release": self.release})
        self.blob.save()
        self._save(force)

    def releases(self):
        return self.all_releases(self.package)

    @classmethod
    def delete(cls, package, release, media_type):
        cls._delete(package, release, media_type)

    def _save(self, force=False):
        raise NotImplementedError

    @classmethod
    def all(cls, namespace=None):
        raise NotImplementedError

    @classmethod
    def _fetch(cls, package, release, media_type=DEFAULT_MEDIA_TYPE):
        raise NotImplementedError

    @classmethod
    def _delete(cls, package, release, media_type):
        raise NotImplementedError

    @classmethod
    def all_releases(cls, package, media_type=None):
        raise NotImplementedError

    @classmethod
    def search(cls, query):
        raise NotImplementedError

    @classmethod
    def isdeleted_release(cls, package, release):
        raise NotImplementedError

    @classmethod
    def reindex(cls):
        raise NotImplementedError

    @classmethod
    def dump_all(cls, blob_cls):
        """ produce a dict with all packages """
        raise NotImplementedError

    @classmethod
    def manifests(cls, package, release):
        raise NotImplementedError
