from __future__ import absolute_import, division, print_function

import re

import appr.semver as semver
from appr.exception import Unsupported
from appr.models.kv.models_index_base import ModelsIndexBase
from appr.models.package_base import PackageBase


class PackageKvBase(PackageBase):
    index_class = ModelsIndexBase

    @property
    def index(self):
        return self.index_class(self.package)

    @classmethod
    def _fetch(cls, package, release, media_type='kpm'):
        index = cls.index_class(package)
        return index.release(release, media_type)

    # def channels(self, channel_class, iscurrent=True):
    #     return self.index.release_channels(self.release)

    @classmethod
    def all_releases(cls, package, media_type=None):
        index = cls.index_class(package)
        return index.releases(media_type)

    @classmethod
    def dump_all(cls, blob_cls):
        index = cls.index_class()
        result = []
        for package_info in index.packages():
            package_name = package_info['namespace'] + "/" + package_info['name']
            releaseindex = cls.index_class(package_name)
            for release in releaseindex.releases():
                for _, package_data in releaseindex.release_manifests(release).iteritems():
                    package_data['channels'] = releaseindex.release_channels(release)
                    package_data['blob'] = releaseindex.get_blob(package_data['content']['digest'])
                    result.append(package_data)
        return result

    @classmethod
    def all(cls, namespace=None, media_type=None, search=None, **kwargs):
        index = cls.index_class()
        result = []
        matching = None
        if search:
            matching = cls.search(search)
        for package_data in index.packages(namespace):
            namespace, name = package_data['namespace'], package_data['name']
            package_name = "%s/%s" % (namespace, name)

            if matching is not None and package_name not in matching:
                continue

            created_at = package_data['created_at']
            releaseindex = cls.index_class(package_name)
            available_releases = [
                str(x)
                for x in sorted(
                    semver.versions(releaseindex.releases(media_type=media_type), False),
                    reverse=True)
            ]  # yapf: disable
            if not available_releases:
                continue

            if media_type is None:
                manifest_list = cls.manifests(package_name, available_releases[0])
            else:
                manifest_list = [media_type]

            view = {
                'releases': available_releases,
                'default': available_releases[0],
                'manifests': manifest_list,
                'name': package_name,
                'visibility': 'public',
                'created_at': created_at}
            result.append(view)
        return result

    @classmethod
    def isdeleted_release(cls, package, release):
        """ TODO """
        return False

    def _save(self, force=False, **kwargs):
        return self.index.add_release(self.data, self.release, self.media_type, force)

    @classmethod
    def search(cls, query, **kwargs):
        index = cls.index_class()
        searchindex = '\n'.join(index.package_names())
        return re.findall(r"(.*%s.*)" % query, searchindex)

    @classmethod
    def _delete(cls, package, release, media_type):
        index = cls.index_class(package)
        return index.delete_release(release, media_type)

    @classmethod
    def reindex(cls):
        raise Unsupported("Reindex is not yet supported")

    @classmethod
    def manifests(cls, package, release):
        index = cls.index_class(package)
        return index.release_manifests(release).keys()
