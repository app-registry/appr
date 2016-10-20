import re
import datetime
import semantic_version
from cnr.semver import last_version, select_version
from cnr.exception import (InvalidVersion,
                           PackageAlreadyExists,
                           raise_package_not_found,
                           PackageVersionNotFound)
from cnr.models import DEFAULT_MEDIA_TYPE
from cnr.models.blob_base import BlobBase

SCHEMA_VERSION = "v1"


class PackageBase(object):

    def __init__(self, package_name, version=None,
                 media_type=DEFAULT_MEDIA_TYPE, blob=None):
        self.package = package_name
        self.media_type = media_type
        self.namespace, self.name = package_name.split("/")
        self.version = version
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
            if self.version in releases:
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
        for release in cls.all_versions(package):
            result.append(cls.view_manifests(package, release))
        return result

    @property
    def data(self):
        if self._data is None:
            self._data = {'created_at': datetime.datetime.utcnow().isoformat()}
        d = {"package": self.package,
             "release": self.version,
             "mediaType": self.manifest_media_type,
             "content": self.content_descriptor()}
        self._data.update(d)
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self.created_at = data['created_at']
        self.version = data['release']
        self._digest = data['content']['digest']
        self._blob_size = data['content']['size']
        self.set_media_type(data['mediaType'])

    @classmethod
    def check_version(cls, version):
        try:
            semantic_version.Version(version)
        except ValueError as e:
            raise InvalidVersion(e.message, {"version": version})
        return None

    @classmethod
    def get(cls, package, version='default', media_type=DEFAULT_MEDIA_TYPE):
        """
        package: string following "namespace/package_name" format
        version: version query. If None return latest version

        returns: (package blob(targz) encoded in base64, version)
        """
        p = cls(package, version)
        p.pull(version, media_type)
        return p

    @classmethod
    def get_version(cls, package, version_query, stable=False):
        versions = cls.all_versions(package)
        if not versions:
            raise_package_not_found(package, version=version_query)
        if version_query is None or version_query == 'default':
            return last_version(versions, stable)
        else:
            try:
                return select_version(versions, str(version_query), stable)
            except ValueError as e:
                raise InvalidVersion(e.message, {"version": version_query})

    def pull(self, version_query=None, media_type=DEFAULT_MEDIA_TYPE):
        if version_query is None:
            version_query = self.version
        package = self.package
        version = self.get_version(package, version_query)
        if version is None:
            raise PackageVersionNotFound("No version match '%s' for package '%s'" % (version_query, package),
                                         {"package": package, "version_query": version_query})

        self.data = self._fetch(package, str(version), media_type)
        return self

    def save(self, force=False):
        self.check_version(self.version)
        if self.isdeleted_release(self.package, self.version) and not force:
            raise PackageAlreadyExists("Package release %s existed" % self.package,
                                       {"package": self.package, "version": self.version})
        self.blob.save()
        self._save(force)

    def versions(self):
        return self.all_versions(self.package)

    @classmethod
    def delete(cls, package, version, media_type):
        cls._delete(package, version, media_type)

    def _save(self, force=False):
        raise NotImplementedError

    @classmethod
    def all(cls, namespace=None):
        raise NotImplementedError

    @classmethod
    def _fetch(cls, package, version, media_type=DEFAULT_MEDIA_TYPE):
        raise NotImplementedError

    @classmethod
    def _delete(cls, package, version, media_type):
        raise NotImplementedError

    @classmethod
    def all_versions(cls, package, media_type=None):
        raise NotImplementedError

    @classmethod
    def search(cls, query):
        raise NotImplementedError

    @classmethod
    def isdeleted_release(cls, package, version):
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
