from __future__ import absolute_import, division, print_function

import json
import os

from appr.exception import Forbidden, PackageAlreadyExists
from appr.models.blob_base import BlobBase
from appr.models.channel_base import ChannelBase
from appr.models.package_base import PackageBase


class ApprDB(object):
    Channel = ChannelBase
    Package = PackageBase
    Blob = BlobBase

    @classmethod
    def restore_backup(cls, data):
        """ bulk add data in db """
        i = 0
        size = len(data['packages'])
        for package_data in data['packages']:
            i += 1
            package = cls.Package(package_data['package'], package_data['release'])

            package.data = package_data
            package.blob = cls.Blob(package.package, package_data['blob'])
            try:
                package.save(False)

                # print '%s/%s  restored: %s(%s) - %s' % (str(i), str(size),
                #                                        package.package, package.release, package.media_type)
            except PackageAlreadyExists:
                pass
                # print '%s/%s  existed: %s(%s) - %s' % (str(i), str(size),
                #                                   package.package, package.release, package.media_type)

            for channel_name in package_data['channels']:
                channel = cls.Channel(channel_name, package.package)
                channel.add_release(package.release, cls.Package)
                # print "%s/%s  restored-channel-release: %s, %s, %s" % (str(i), str(size),
                #                                                       channel.package, channel.name, package.release)

        i = 0
        size = len(data['channels'])
        for channel_data in data['channels']:
            i += 1
            channel = cls.Channel(channel_data['name'], channel_data['package'])
            channel.add_release(channel_data['current'], cls.Package)
            print("%s/%s  restored-channel: %s" % (str(i), str(size), channel.name))

    @classmethod
    def restore_backup_from_file(cls, filepath):
        """ bulk add data in db """
        with open(filepath, 'rb') as f:
            data = json.load(f)
        return cls.restore_backup(data)

    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("APPR_DB_ALLOW_RESET", "false") == "true" or force:
            raise NotImplementedError
        else:
            raise Forbidden("Reset DB is deactivated")

    @classmethod
    def backup(cls):
        data = {'packages': cls.Package.dump_all(cls.Blob), 'channels': cls.Channel.dump_all()}
        return data

    @classmethod
    def backup_to_file(cls, filepath):
        with open(filepath, 'wb') as f:
            json.dump(cls.backup(), f)
