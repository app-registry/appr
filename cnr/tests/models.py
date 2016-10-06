import pytest
from cnr.exception import (InvalidVersion,
                           PackageAlreadyExists,
                           PackageVersionNotFound,
                           Forbidden,
                           ChannelNotFound,
                           ChannelAlreadyExists,
                           PackageNotFound)


@pytest.mark.models
class CnrTestModels:
    from cnr.models.db_base import CnrDB
    DB_CLASS = CnrDB

    @pytest.fixture()
    def db(self):
        return self.DB_CLASS

    def test_package_init(self, db_class):
        p = db_class.Package("titi/toot", '1.2.0', 'helm')
        assert p.name == "toot"
        assert p.namespace == "titi"
        assert p.version == "1.2.0"
        assert p.package == "titi/toot"

    def test_package_set_blob(self, db_class, package_b64blob):
        p = db_class.Package("titi/toot", '1.2.0', 'helm', None)
        assert p._data is None
        p.blob = package_b64blob
        assert p.data['blob'] == package_b64blob
        assert p.data['digest'] == "8dc8a2c479f770fd710e0dddaa7af0e6b495bc6375cdf2b4a649f4c2b03e27d5"

    @pytest.mark.integration
    def test_db_restore(self, newdb, dbdata1):
        assert newdb.Package.dump_all() == []
        assert newdb.Channel.dump_all() == []
        newdb.restore_backup(dbdata1)
        assert sorted(newdb.Package.dump_all()) == sorted(dbdata1['packages'])
        assert sorted(newdb.Channel.dump_all()) == sorted(dbdata1['channels'])

    @pytest.mark.integration
    def test_get_default_package(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat", 'default', 'kpm')
        assert p.package == "titi/rocketchat"

    @pytest.mark.integration
    def test_get_package_version_query(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat", ">1.2", 'kpm')
        assert p.package == "titi/rocketchat"
        assert p.version == "2.0.1"
        assert p.digest == "d3b54b7912fe770a61b59ab612a442eac52a8a5d8d05dbe92bf8f212d68aaa80"
        assert p.blob is not None

    @pytest.mark.integration
    def test_get_package_absent_manifest(self, db_with_data1):
        with pytest.raises(PackageNotFound):
            db_with_data1.Package.get("titi/rocketchat", ">1.2", 'bad')

    @pytest.mark.integration
    def test_get_package_absent_version(self, db_with_data1):
        with pytest.raises(PackageVersionNotFound):
            db_with_data1.Package.get("titi/rocketchat", "2.0.2", 'kpm')

    @pytest.mark.integration
    def test_get_package_bad_version_query(self, db_with_data1):
        with pytest.raises(InvalidVersion):
            db_with_data1.Package.get("titi/rocketchat", "abc", 'kpm')

    @pytest.mark.integration
    def test_pull_package_absent_version(self, db_with_data1):
        with pytest.raises(PackageVersionNotFound):
            p = db_with_data1.Package("titi/rocketchat", '4.3.0', 'kpm')
            p.pull()

    @pytest.mark.integration
    def test_save_package_bad_version(self, newdb):
        assert newdb.Package.all() == []
        with pytest.raises(InvalidVersion):
            p = newdb.Package("titi/rocketchat", 'abc', 'kpm')
            p.save()

    @pytest.mark.integration
    def test_save_package(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', package_b64blob)
        p.save()
        assert newdb.Package.get('titi/rocketchat', '2.3.4', 'kpm').blob == package_b64blob

    @pytest.mark.integration
    def test_save_package_exists(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', package_b64blob)
        p.save()
        assert newdb.Package.get("titi/rocketchat", "2.3.4") is not None
        with pytest.raises(PackageAlreadyExists):
            p.save()

    @pytest.mark.integration
    def test_save_package_exists_force(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', package_b64blob)
        p.save()
        p.save(True)

    # @TODO store deleted releases
    @pytest.mark.integration
    @pytest.mark.xfail
    def test_save_package_deleted(self, newdb, package_b64blob):
        assert newdb.Package.all() == []
        p = newdb.Package("titi/rocketchat", '2.3.4', 'kpm', package_b64blob)
        p.save()
        newdb.Package.delete("titi/rocketchat", '2.3.4', 'kpm')
        with pytest.raises(PackageAlreadyExists):
            p.save()

    @pytest.mark.integration
    def test_list_package_versions(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat")
        assert sorted(p.versions()) == sorted(['0.0.1', '1.0.1', '2.0.1'])

    @pytest.mark.integration
    def test_list_package_channels(self, db_with_data1):
        p = db_with_data1.Package.get("titi/rocketchat", '2.0.1')
        assert p.channels() == ['stable']
        p2 = db_with_data1.Package.get("titi/rocketchat", '1.0.1')
        assert sorted(p2.channels()) == sorted(['stable', 'dev'])
        p3 = db_with_data1.Package.get("titi/rocketchat", '0.0.1')
        assert sorted(p3.channels()) == sorted([])

    def test_forbiddeb_db_reset(self, db_class):
        with pytest.raises(Forbidden):
            db_class.reset_db()

    @pytest.mark.integration
    def test_all_channels(self, db_with_data1):
        channels = [c.name for c in db_with_data1.Channel.all('titi/rocketchat')]
        assert sorted(channels) == [u'default', u'dev', u'stable']

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
        channel = db_with_data1.Channel('stable', 'titi/rocketchat')
        assert sorted(channel.releases()) == sorted([u'1.0.1', u'2.0.1'])

    @pytest.mark.integration
    def test_channel_no_releases(self, db_with_data1):
        channel = db_with_data1.Channel('default', 'titi/rocketchat')
        assert sorted(channel.releases()) == sorted([])

    @pytest.mark.integration
    def test_channel_add_release(self, db_with_data1):
        channel = db_with_data1.Channel('default', 'titi/rocketchat')
        package = db_with_data1.Package.get('titi/rocketchat', '1.0.1')
        assert sorted(channel.releases()) == sorted([])
        assert 'default' not in package.channels()
        channel.add_release('1.0.1', db_with_data1.Package)
        assert sorted(channel.releases()) == sorted(['1.0.1'])
        assert "default" in package.channels()

    @pytest.mark.integration
    def test_channel_add_release_new_channel(self, db_with_data1):
        channel = db_with_data1.Channel('newone', 'titi/rocketchat')
        assert channel.exists() is False
        package = db_with_data1.Package.get('titi/rocketchat', '1.0.1')
        assert sorted(channel.releases()) == sorted([])
        assert 'newone' not in package.channels()
        channel.add_release('1.0.1', db_with_data1.Package)
        assert sorted(channel.releases()) == sorted(['1.0.1'])
        assert "newone" in package.channels()
        assert channel.exists() is True

    @pytest.mark.integration
    def test_channel_delete_releases(self, db_with_data1):
        channel = db_with_data1.Channel('stable', 'titi/rocketchat')
        package = db_with_data1.Package.get('titi/rocketchat', '1.0.1')
        assert sorted(channel.releases()) == sorted([u'1.0.1', u'2.0.1'])
        assert 'stable' in package.channels()
        channel.remove_release('1.0.1')
        assert sorted(channel.releases()) == sorted(['2.0.1'])
        assert "stable" not in package.channels()

    @pytest.mark.integration
    def test_channel_delete_absent_releases(self, db_with_data1):
        channel = db_with_data1.Channel('new', 'titi/rocketchat')
        with pytest.raises(ChannelNotFound):
            channel.remove_release('1.0.1')

    @pytest.mark.integration
    def test_channel_add_bad_releases(self, db_with_data1):
        channel = db_with_data1.Channel('stable', 'titi/rocketchat')
        db_with_data1.Package.get('titi/rocketchat', '1.0.1')
        with pytest.raises(InvalidVersion):
            channel.add_release('1.a.1', db_with_data1.Package)

    @pytest.mark.integration
    def test_channel_add_absent_releases(self, db_with_data1):
        channel = db_with_data1.Channel('stable', 'titi/rocketchat')
        db_with_data1.Package.get('titi/rocketchat', '1.0.1')
        with pytest.raises(PackageVersionNotFound):
            channel.add_release('1.4.1', db_with_data1.Package)

    @pytest.mark.integration
    def test_create_channel(self, db_with_data1):
        channel = db_with_data1.Channel('newone', 'titi/rocketchat')
        channels = [c.name for c in db_with_data1.Channel.all('titi/rocketchat')]
        assert "newone" not in channels
        channel.save()
        channels = [c.name for c in db_with_data1.Channel.all('titi/rocketchat')]
        assert "newone" in channels

    @pytest.mark.integration
    def test_create_channel_already_exists(self, db_with_data1):
        channel = db_with_data1.Channel('newone', 'titi/rocketchat')
        channel.save()
        with pytest.raises(ChannelAlreadyExists):
            channel.save()

    @pytest.mark.integration
    def test_create_channel_already_exists_force(self, db_with_data1):
        channel = db_with_data1.Channel('newone', 'titi/rocketchat')
        channel.save()
        channel.save(True)

    @pytest.mark.integration
    def test_create_channel_absent_package(self, db_with_data1):
        channel = db_with_data1.Channel('newone', 'titi/doest')
        with pytest.raises(PackageNotFound):
            channel.save()

    @pytest.mark.integration
    def test_channel_current_release(self, db_with_data1):
        channel = db_with_data1.Channel('stable', 'titi/rocketchat')
        assert channel.current_release() == '2.0.1'

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
