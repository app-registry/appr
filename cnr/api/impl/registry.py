import logging
import cnr.semver as semver


logger = logging.getLogger(__name__)


def _get_package(package, version_query, package_class):
    """
      Fetch the package data from the datastore
      and instantiate a :obj:`cnr.models.package_base.PackageModelBase`

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version_query (:obj:`str`): a version query, eg: ">=1.5,<2.0"
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`cnr.kub_jsonnet.KubJsonnet`: :obj:`cnr.models.package_base.PackageModelBase`

    See Also:
       * :obj:`cnr.api.models.package_base.PackageModelBase`
       * :obj:`cnr.api.models.etcd.package.Package`

    Raises:
      :obj:`cnr.exception.PackageNotFound`: package not found
      :obj:`cnr.exception.InvalidVersion`: version-query malformated
      :obj:`cnr.exception.PackageVersionNotFound`: version-query didn't match any release

    """

    if version_query is None:
        version_query = 'default'
    p = package_class.get(package, version_query)
    return p


def pull(package, version, package_class):
    """
    Retrives the package blob from the datastore

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version_query (:obj:`str`): a version query, eg: ">=1.5,<2.0"
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: package data
        * package: package name
        * version: version that matched the version query
        * filename: suggested filename to create the tarball
        * blob: a `tar.gz` encoded in base64.

    Example:
      >>> cnr.api.impl.registry.pull("coreos/etcd", version=">=3")
        {
         'blob': 'H4sICHDFvlcC/3RpdF9yb2NrZXRjaGF0XzEuMTAuMGt1Yi50YXIA7ZdRb5swEM',
         'filename': u'coreos_etcd_3.0.1.tar.gz',
         'package': 'coreos_etcd',
         'version': u'3.0.1'
        }

    Raises:
      :obj:`cnr.exception.PackageNotFound`: package not found
      :obj:`cnr.exception.InvalidVersion`: version-query malformated
      :obj:`cnr.exception.PackageVersionNotFound`: version-query didn't match any release

    See Also:
       * :obj:`cnr.api.registry.pull`

    """

    packagemodel = _get_package(package, version, package_class=package_class)
    resp = {"package": package,
            "blob": packagemodel.blob,
            "version": packagemodel.version,
            "filename": "%s_%s.tar.gz" % (packagemodel.package.replace("/", "_"), packagemodel.version)}
    return resp


def push(package, version, blob, force, package_class):
    """
    Push a new package release in the the datastore

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version (:obj:`str`): the 'exact' package version (this is not a version_query)
      blob (:obj:`str`): the package directory in `tar.gz` and encoded in base64
      force (:obj:`boolean`): if the package exists already, overwrite it
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: push status

    Example:
      >>> cnr.api.impl.registry.push("coreos/etcd", "3.0.1",
            "H4sICHDFvlcC/3RpdF9yb2NrZXRjaGF0XzEuMTAuMGt1Yi50YXIA7ZdRb5swEM")
        {
         'status': u'ok'
        }

    Raises:
      PackageAlreadyExists: if package already exists and `force` is False

    See Also:
       * :obj:`cnr.api.registry.push`

    """
    p = package_class(package, version, blob)
    p.save(force=force)
    return {"status": "ok"}


def search_reindex(package_class):
    package_class.reindex()
    return {"status": "ok"}


def search(query, package_class):
    """
    Search packages

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`list`: list of package names

    Example:
      >>> cnr.api.impl.registry.search("etcd")
        [
         'coreos/etcd',
         'ant31/etcd',
         'my-etcd/stable'
        ]

    See Also:
       * :obj:`cnr.api.registry.search`

    """
    p = package_class.search(query)
    return p


def list_packages(namespace, package_class):
    """
    List all packages, filters can be applied
    Must have at least a release to be visible

    Todos:
       - sort_by: name, created_at, downloads, number of stars
       - filter_by: users

    Args:
      namespace (:obj:`str`): returns packages from the `namespace` only
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`list of dict`: list packages
        * name: package name
        * available_releases (list of str):  All releases
        * created_at (datetime, optional): package creation date
        * downloads (int, optional): number of downloads
        * version: release name

    Example:
      >>> cnr.api.impl.registry.list_packages()
      [
       {
        'available_releases': ['0.1.0'],
        'name': u'quentinm/rados-gateway',
        'version': '0.1.0',
        'created_at": "2016-04-22T11:58:34.103Z",
        'downloads': 41
       },
       {
        'available_releases': ['0.1.0'],
        'name': u'quentinm/nova',
        'version': '0.1.0'
       },
      ]

    See Also:
       * :obj:`cnr.api.registry.list_packages`
    """
    resp = package_class.all(namespace)
    return resp


def show_package(package,
                 version,
                 channel_class,
                 package_class):
    """
    Returns package details

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version (:obj:`str`): the 'exact' package version (this is not a version_query)
      channel_class (:obj:`cnr.models.channel_base:ChannelBase`): the implemented Channel class to use
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: package data
        * version (str)
        * name (str)
        * created_at (str)
        * digest (str)
        * channels (list)
        * available_releases (list)
        * dependencies (list)
        * variables (dict)
        * manifest (str)

    Example:
      >>> cnr.api.impl.registry.show_package("ns/mypackage")
      {
      "version": "3.2.0-rc",
      "name": "ns/mypackage",
      "created_at": "2016-08-25T10:16:16.366758",
      "digest": "93de60f59238f9aebce5b9f8bc708e02a0d740364fcd4b185c6da7fc1cdfe1ba",
      "channels": ['stable', 'beta'],
      "available_releases": [
        "3.2.0-rc"
        "3.1.0",
        "3.0.1"
      ],
      "dependencies": [
        "ns/dep1",
        "ns/dep2",
        "ns/dep3"
       ],
       "variables": {
         "replicas": 1,
         "image": "ns/mypackage:latest",
         "namespace": "default",
         "cluster": "cluster.local",
         "mail_url": "smtp://"
       },
      "manifest": "---...."
       }

    Raises:
      :obj:`cnr.exception.PackageNotFound`: package not found
      :obj:`cnr.exception.InvalidVersion`: version-query malformated
      :obj:`cnr.exception.PackageVersionNotFound`: version-query didn't match any release

    See Also:
       * :obj:`cnr.api.registry.show_package`
    """
    stable = False
    packagemodel = _get_package(package, version, package_class)
    manifest = packagemodel.manifest()
    response = {"manifest": packagemodel.packager.manifest,
                "version": packagemodel.version,
                "name":  package,
                "created_at": packagemodel.created_at,
                "digest": packagemodel.digest,
                "variables": manifest.variables,
                "dependencies": manifest.dependencies,
                "channels": packagemodel.channels(channel_class),
                "available_releases": [str(x) for x in sorted(semver.versions(packagemodel.versions(), stable),
                                                              reverse=True)]}
    return response


# CHANNELS
def list_channels(package, channel_class):
    """
    List all channels for a given package

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      channel_class (:obj:`cnr.models.channel_base:ChannelBase`): the implemented Channel class to use

    Returns:
      :obj:`list of dict`: list channels:
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> cnr.api.impl.registry.list_channels("myns/package")
      [{'channel': u'stable', 'current': '1.10.2', 'releases': [u'1.10.2']},
       {'channel': u'dev', 'current': 2.0.0-beta, 'releases': [1.10.2, 2.0.0-beta]}]

    See Also:
       * :obj:`cnr.api.registry.list_channels`
    """
    channels = channel_class.all_channels(package).values()
    return channels


def show_channel(package, name, channel_class):
    """
    Show channel info
    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      name (:obj:`str`): channel name to inspect
      channel_class (:obj:`cnr.models.channel_base:ChannelBase`): the implemented Channel class to use

    Returns:
      :obj:`dict`: channel info
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> cnr.api.impl.registry.list_channels("tit/rocketchat", 'dev')
      {'channel': u'dev', 'current': '2.0.0-beta', 'releases': [u'1.10.2']}

    Raises:
      :obj:`cnr.api.exception.ChannelNotFound`: channel not found

    See Also:
       * :obj:`cnr.api.registry.show_channel`
    """
    c = channel_class(name, package)
    return c.to_dict()


def add_channel_release(package, name, release, channel_class, package_class):
    """
    Add a package-release to a channel
    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      name (:obj:`str`): channel name to inspect
      release (:obj:`str`): package version to add
      channel_class (:obj:`cnr.models.channel_base:ChannelBase`): the implemented Channel class to use
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: channel info
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> cnr.api.impl.registry.list_channels("tit/rocketchat", 'dev')
      {'channel': u'dev', 'current': '2.0.0-beta', 'releases': [u'1.10.2']}

    Raises:
      :obj:`cnr.api.exception.ChannelNotFound`: channel not found

    See Also:
       * :obj:`cnr.api.registry.add_channel_release`
    """
    channel = channel_class(name, package)
    channel.add_release(release, package_class)
    return channel.to_dict()


def delete_channel_release(package, name, release, channel_class, package_class):
    """
    Remove a release from a channel

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      name (:obj:`str`): channel name to inspect
      release (:obj:`str`): package version to add
      channel_class (:obj:`cnr.models.channel_base:ChannelBase`): the implemented Channel class to use
      package_class (:obj:`cnr.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: channel info
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> cnr.api.impl.registry.list_channels("tit/rocketchat", 'dev')
      {'channel': u'dev', 'current': '2.0.0-beta', 'releases': [u'1.10.2']}

    Raises:
      :obj:`cnr.api.exception.ChannelNotFound`: channel not found

    See Also:
       * :obj:`cnr.api.registry.delete_channel_release`
    """
    channel = channel_class(name, package)
    channel.remove_release(release)
    return channel.to_dict()


def create_channel(package, name, channel_class):
    channel = channel_class(name, package)
    channel.save()
    return channel.to_dict()


def delete_channel(package, name, channel_class):
    channel = channel_class(name, package)
    channel.delete()
    return {"channel": channel.name, "package": package, "action": 'delete'}


def delete_package(package, version, package_class, channel_class):
    packagemodel = _get_package(package, version, package_class)
    package_class.delete(packagemodel.package, packagemodel.version, channel_class)
    return {"status": "delete", "package": packagemodel.package, "version": packagemodel.version}
