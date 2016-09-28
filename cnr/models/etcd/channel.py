import re
import etcd
from cnr.models.channel_base import ChannelBase
from cnr.models.etcd import etcd_listkeys, ETCD_PREFIX, etcd_client


class Channel(ChannelBase):
    def __init__(self, name, package):
        super(Channel, self).__init__(name, package)

    @classmethod
    def _etcdpath(self, package, name=None):
        path = ETCD_PREFIX + package + "/channels"
        if name is not None:
            path = path + "/%s" % name
        return path

    def _exists(self):
        """ Check if the channel is saved already """
        path = self._etcdpath(self.package, self.name)
        try:
            etcd_client.read(path)
        except etcd.EtcdKeyNotFound:
            return False
        return True

    def save(self):
        path = self._etcdpath(self.package, self.name)
        try:
            etcd_client.write(path, None,  dir=True, prevExist=False)
            return True
        except etcd.EtcdAlreadyExist:
            raise self._raise_already_exists(self.name, self.package)

    def delete(self):
        path = self._etcdpath(self.package, self.name)
        if self.exists:
            etcd_client.delete(path, recursive=True)
            return True
        return False

    @classmethod
    def all(self, package):
        """
        Returns all available channels for a package
        """
        path = self._etcdpath(package)
        try:
            chans = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            return []
        result = []
        for child in chans.children:
            m = re.match("^/%s/([a-zA-Z0-9-_]+)/?.*$" % path, child.key)
            if m is None:
                continue
            channel = m.group(1)
            result.append(channel)
        return result

    def releases(self):
        """ Returns the list of versions """
        path = self._etcdpath(self.package, self.name)
        try:
            releases = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(self.package, self.name)
        result = etcd_listkeys(releases, path)
        return result

    def _add_release(self, version):
        path = self._etcdpath(self.package, "%s/%s" % (self.name, version))
        try:
            n = self._new_chan_release(version)
            etcd_client.write(path, n, prevExist=False)
        except etcd.EtcdAlreadyExist:
            raise self._raise_already_exists(self.name, self.package, version)
        return n

    def _remove_release(self, version):
        path = self._etcdpath(self.package, "%s/%s" % (self.name, version))
        try:
            etcd_client.delete(path)
            return True
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(self.package, self.name, version)

    def activate_release(self, version):
        raise NotImplementedError
