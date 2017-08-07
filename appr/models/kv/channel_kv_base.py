from __future__ import absolute_import, division, print_function

from appr.models.channel_base import ChannelBase
from appr.models.kv.models_index_base import ModelsIndexBase


class ChannelKvBase(ChannelBase):
    index_class = ModelsIndexBase

    @property
    def index(self):
        return self.index_class(self.package)

    @classmethod
    def all(cls, package):
        index = cls.index_class(package)
        result = []
        for channel_data in index.channels():
            channel = cls(channel_data['name'], package, channel_data['current'])
            result.append(channel)
        return result

    @classmethod
    def get(cls, name, package):
        index = cls.index_class(package)
        channel_dict = index.channel(name)
        return cls(name, package, channel_dict['current'])

    def releases(self):
        return self.index.channel_releases(self.name)

    def _remove_release(self, release):
        return self.index.delete_channel_release(self.name, release)

    def _exists(self):
        return self.index.ischannel_exists(self.name)

    def save(self):
        return self.index.add_channel(self.name, self.current)

    def delete(self):
        return self.index.delete_channel(self.name)

    @classmethod
    def dump_all(cls, package_class=None):
        index = cls.index_class()
        result = []
        for package_name in index.package_names():
            packageindex = cls.index_class(package_name)
            result += packageindex.channels()
        return result
