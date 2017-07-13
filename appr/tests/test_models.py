from __future__ import absolute_import, division, print_function

import collections
from operator import itemgetter

import pytest

from appr.exception import (ChannelNotFound, Forbidden, InvalidRelease, PackageAlreadyExists,
                            PackageNotFound, PackageReleaseNotFound)


def convert_utf8(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_utf8, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_utf8, data))
    else:
        return data


@pytest.mark.models
class TestModels:
    from appr.models.kv.filesystem.db import ApprDB
    DB_CLASS = ApprDB

    @pytest.fixture()
    def db(self):
        return self.DB_CLASS

    def test_package_init(self, db_class):
        p = db_class.Package("titi/toot", '1.2.0', 'helm')
        assert p.name == "toot"
        assert p.namespace == "titi"
        assert p.release == "1.2.0"
        assert p.package == "titi/toot"

    def test_package_set_blob(self, db_class, package_b64blob):
        p = db_class.Package("titi/toot", '1.2.0', 'helm', None)
        assert p._data is None
        p.blob = db_class.Blob("titi/rocketchat", package_b64blob)
        assert p.blob.b64blob == package_b64blob
        assert p.data['content'][
            'digest'] == "8dc8a2c479f770fd710e0dddaa7af0e6b495bc6375cdf2b4a649f4c2b03e27d5"
        assert p.blob.digest == "8dc8a2c479f770fd710e0dddaa7af0e6b495bc6375cdf2b4a649f4c2b03e27d5"

    @pytest.mark.integration
    def test_db_restore(self, newdb, dbdata1):
        assert newdb.Package.dump_all(newdb.Blob) == []
        assert newdb.Channel.dump_all(newdb.Blob) == []
        newdb.restore_backup(dbdata1)
        dump = newdb.Package.dump_all(newdb.Blob)
        sorting = itemgetter('package', "mediaType", "release")
        dump = convert_utf8(dump)
        expected_packages = convert_utf8(dbdata1['packages'])
        for x in xrange(len(expected_packages)):
            dump[x].pop("created_at")
            expected_packages[x].pop("created_at")

        assert sorted(dump, key=sorting) == sorted(expected_packages, key=sorting)
        assert sorted(newdb.Channel.dump_all(newdb.Blob)) == sorted(dbdata1['channels'])

    @pytest.mark.integration
    def test_get_default_package(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat", 'default', 'kpm')
        assert p.package == "titi/rocketchat"

    @pytest.mark.integration
    def test_get_package_release_query(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat", ">1.2", 'kpm')
        assert p.package == "titi/rocketchat"
        assert p.release == "2.0.1"
        assert p.digest == "d3b54b7912fe770a61b59ab612a442eac52a8a5d8d05dbe92bf8f212d68aaa80"

    @pytest.mark.integration
    def test_get_blob(self, db_with_data1):
        blob = db_with_data1.Blob.get(
            "titi/rocketchat", "d3b54b7912fe770a61b59ab612a442eac52a8a5d8d05dbe92bf8f212d68aaa80")
        assert blob.digest == "d3b54b7912fe770a61b59ab612a442eac52a8a5d8d05dbe92bf8f212d68aaa80"
        assert blob.size == 778L

    @pytest.mark.integration
    def test_get_package_absent_manifest(self, db_with_data1):
        with pytest.raises(PackageNotFound):
            db_with_data1.Package.get("titi/rocketchat", ">1.2", 'bad')

    @pytest.mark.integration
    def test_get_package_absent_release(self, db_with_data1):
        with pytest.raises(PackageReleaseNotFound):
            db_with_data1.Package.get("titi/rocketchat", "2.0.2", 'kpm')

    @pytest.mark.integration
    def test_get_package_bad_release_query(self, db_with_data1):
        with pytest.raises(InvalidRelease):
            db_with_data1.Package.get("titi/rocketchat", "abc", 'kpm')

    @pytest.mark.integration
    def test_pull_package_absent_release(self, db_with_data1):
        with pytest.raises(PackageReleaseNotFound):
            p = db_with_data1.Package("titi/rocketchat", '4.3.0', 'kpm')
            p.pull()

    @pytest.mark.integration
    def test_save_package_bad_release(self, newdb):
        assert newdb.Package.all() == []
        with pytest.raises(InvalidRelease):
            p = newdb.Package("titi/rocketchat", 'abc', 'kpm')
            p.save()

    @pytest.mark.integration
    def test_save_package(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        blob = newdb.Blob("titi/rocketchat", package_b64blob)
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', blob)
        p.save()
        fetchpackage = newdb.Package.get('titi/rocketchat', '2.3.4', 'kpm')
        assert fetchpackage.digest == "8dc8a2c479f770fd710e0dddaa7af0e6b495bc6375cdf2b4a649f4c2b03e27d5"
        assert newdb.Blob.get('titi/rocketchat',
                              fetchpackage.digest).size == fetchpackage.blob_size

    @pytest.mark.integration
    def test_save_package_exists(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        blob = newdb.Blob("titi/rocketchat", package_b64blob)
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', blob)
        p.save()
        assert newdb.Package.get("titi/rocketchat", "2.3.4", "kpm") is not None
        with pytest.raises(PackageAlreadyExists):
            p.save()

    @pytest.mark.integration
    def test_save_package_exists_force(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        blob = newdb.Blob("titi/rocketchat", package_b64blob)
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', blob)
        p.save()
        p.save(True)

    # @TODO store deleted releases
    @pytest.mark.integration
    @pytest.mark.xfail
    def test_save_package_deleted(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        blob = newdb.Blob("titi/rocketchat", package_b64blob)
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', blob)
        p.save()
        newdb.Package.delete("titi/rocketchat", '2.3.4', 'kpm')
        with pytest.raises(PackageAlreadyExists):
            p.save()

    @pytest.mark.integration
    def test_list_package_releases(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat", "default", "kpm")
        assert sorted(p.releases()) == sorted(['0.0.1', '1.0.1', '2.0.1'])

    @pytest.mark.integration
    def test_list_package_channels(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat", '2.0.1', "kpm")
        assert p.channels(db_with_data1.Channel) == ['stable']
        p2 = db_with_data1.Package.get("titi/rocketchat", '1.0.1', "kpm")
        assert sorted(p2.channels(db_with_data1.Channel)) == sorted(['dev'])
        assert sorted(p2.channels(db_with_data1.Channel, iscurrent=False)) == sorted([
            'dev', 'stable'])
        p3 = db_with_data1.Package.get("titi/rocketchat", '0.0.1', "kpm")
        assert sorted(p3.channels(db_with_data1.Channel)) == sorted([])

    def test_forbiddeb_db_reset(self, db_class):
        with pytest.raises(Forbidden):
            db_class.reset_db()

    @pytest.mark.integration
    def test_all_channels(self, db_with_data1):
        channels = [c.name for c in db_with_data1.Channel.all('titi/rocketchat')]
        assert sorted(channels) == sorted([u'dev', u'stable'])

    @pytest.mark.integration
    def test_all_channels_absent_package(self, db_with_data1):
        with pytest.raises(PackageNotFound):
            db_with_data1.Channel.all('titi/doesntexists')

    @pytest.mark.integration
    def test_all_channels_no_data(self, newdb):
        with pytest.raises(PackageNotFound):
            newdb.Channel.all('titi/doesntexists')

    @pytest.mark.integration
    def test_channel_releases(self, db_with_data1):
        channel = db_with_data1.Channel.get('stable', 'titi/rocketchat')
        assert sorted(channel.releases()) == sorted([u'1.0.1', u'2.0.1'])

    @pytest.mark.integration
    def test_channel_no_releases(self, db_with_data1):
        channel = db_with_data1.Channel('default', 'titi/rocketchat')
        with pytest.raises(ChannelNotFound):
            channel.releases()

    @pytest.mark.integration
    def test_channel_add_release(self, db_with_data1):
        channel = db_with_data1.Channel('default', 'titi/rocketchat')
        package = db_with_data1.Package.get('titi/rocketchat', '1.0.1', "kpm")
        with pytest.raises(ChannelNotFound):
            channel.releases()
        assert 'default' not in package.channels(db_with_data1.Channel)
        channel.add_release('1.0.1', db_with_data1.Package)
        assert sorted(channel.releases()) == sorted(['1.0.1'])
        assert "default" in package.channels(db_with_data1.Channel)

    @pytest.mark.integration
    def test_channel_add_release_new_channel(self, db_with_data1):
        channel = db_with_data1.Channel('newone', 'titi/rocketchat')
        assert channel.exists() is False
        package = db_with_data1.Package.get('titi/rocketchat', '1.0.1', "kpm")
        assert 'newone' not in package.channels(db_with_data1.Channel)
        channel.add_release('1.0.1', db_with_data1.Package)
        assert sorted(channel.releases()) == sorted(['1.0.1'])
        assert "newone" in package.channels(db_with_data1.Channel)
        assert channel.exists() is True

    @pytest.mark.integration
    def test_channel_delete_releases(self, db_with_data1):
        channel = db_with_data1.Channel.get('stable', 'titi/rocketchat')
        package = db_with_data1.Package.get('titi/rocketchat', '2.0.1', "kpm")
        assert sorted(channel.releases()) == sorted([u'1.0.1', u'2.0.1'])
        assert 'stable' in package.channels(db_with_data1.Channel)
        assert channel.current == "2.0.1"
        channel.remove_release('2.0.1')
        assert sorted(channel.releases()) == sorted(['1.0.1'])
        channel = db_with_data1.Channel.get('stable', 'titi/rocketchat')
        assert channel.current is not None
        assert "stable" not in package.channels(db_with_data1.Channel)

    @pytest.mark.integration
    def test_channel_delete_all_releases(self, db_with_data1):
        channel = db_with_data1.Channel.get('dev', 'titi/rocketchat')
        package = db_with_data1.Package.get('titi/rocketchat', '1.0.1', "kpm")
        assert sorted(channel.releases()) == sorted([u'1.0.1'])
        assert 'dev' in package.channels(db_with_data1.Channel)
        assert channel.current == "1.0.1"
        channel.remove_release('1.0.1')
        with pytest.raises(ChannelNotFound):
            channel = db_with_data1.Channel.get('dev', 'titi/rocketchat')

    @pytest.mark.integration
    def test_channel_delete_absent_releases(self, db_with_data1):
        channel = db_with_data1.Channel('new', 'titi/rocketchat')
        with pytest.raises(ChannelNotFound):
            channel.remove_release('1.0.1')

    @pytest.mark.integration
    def test_channel_add_bad_releases(self, db_with_data1):
        channel = db_with_data1.Channel('stable', 'titi/rocketchat')
        db_with_data1.Package.get('titi/rocketchat', '1.0.1', "kpm")
        with pytest.raises(InvalidRelease):
            channel.add_release('1.a.1', db_with_data1.Package)

    @pytest.mark.integration
    def test_channel_add_absent_releases(self, db_with_data1):
        channel = db_with_data1.Channel('stable', 'titi/rocketchat')
        db_with_data1.Package.get('titi/rocketchat', '1.0.1', "kpm")
        with pytest.raises(PackageReleaseNotFound):
            channel.add_release('1.4.1', db_with_data1.Package)

    @pytest.mark.integration
    def test_create_channel_absent_package(self, db_with_data1):
        channel = db_with_data1.Channel('newone', 'titi/doest')
        with pytest.raises(PackageNotFound):
            channel.save()

    @pytest.mark.integration
    def test_channel_current_release(self, db_with_data1):
        channel = db_with_data1.Channel.get('stable', 'titi/rocketchat')
        assert channel.current_release() == '2.0.1'

    @pytest.mark.integration
    def test_get_channel_absent(self, db_with_data1):
        with pytest.raises(ChannelNotFound):
            db_with_data1.Channel.get('stableh', 'titi/rocketchat')

    # @todo better all test
    @pytest.mark.integration
    def test_list_all_package(self, db_with_data1):
        result = sorted(db_with_data1.Package.all())
        assert len(result) == 1

    @pytest.mark.integration
    def test_search_empty_package(self, db_with_data1):
        assert db_with_data1.Package.search('fdsf') == []

    @pytest.mark.integration
    def test_search_package(self, db_with_data1):
        assert db_with_data1.Package.search('rocket') == ['titi/rocketchat']


ApprTestModels = TestModels
