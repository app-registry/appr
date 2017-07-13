from __future__ import absolute_import, division, print_function


class ApprException(Exception):
    status_code = 500
    errorcode = "internal-error"

    def __init__(self, message, payload=None):
        super(ApprException, self).__init__()
        self.payload = dict(payload or ())
        self.message = message

    def to_dict(self):
        return {"code": self.errorcode, "message": self.message, "details": self.payload}

    def __str__(self):
        return self.message


class InvalidUsage(ApprException):
    status_code = 400
    errorcode = "invalid-usage"


class InvalidRelease(ApprException):
    status_code = 422
    errorcode = "invalid-release"


class InvalidParams(ApprException):
    status_code = 422
    errorcode = "invalid-parameters"


class PackageAlreadyExists(ApprException):
    status_code = 409
    errorcode = "package-exists"


class PackageNotFound(ApprException):
    status_code = 404
    errorcode = "package-not-found"


class ResourceNotFound(ApprException):
    status_code = 404
    errorcode = "resource-not-found"


class ChannelNotFound(ApprException):
    status_code = 404
    errorcode = "channel-not-found"


class Forbidden(ApprException):
    status_code = 403
    errorcode = "forbidden"


class PackageReleaseNotFound(ApprException):
    status_code = 404
    errorcode = "package-release-not-found"


class UnauthorizedAccess(ApprException):
    status_code = 401
    errorcode = "unauthorized-access"


class Unsupported(ApprException):
    status_code = 501
    errorcode = "unsupported"


class UnableToLockResource(ApprException):
    status_code = 409
    errorcode = "resource-in-use"


class InvalidVersion(ApprException):
    status_code = 422
    errorcode = "invalid-version"


class PackageVersionNotFound(ApprException):
    status_code = 404
    errorcode = "package-version-not-found"


def raise_package_not_found(package, release=None, media_type=None):
    raise PackageNotFound("package %s doesn't exist, v: %s, type: %s" % (package, str(release),
                                                                         str(media_type)),
                          {'package': package,
                           'release': release,
                           'media_type': media_type})


def raise_channel_not_found(package, channel=None, release=None):
    if channel is None:
        raise ChannelNotFound("No channel found for package '%s'" % (package), {
            'package': package})
    else:
        raise ChannelNotFound("Channel '%s' doesn't exist for package '%s'" % (channel, package), {
            'channel': channel,
            'package': package,
            'release': release})


def raise_package_exists(package, release, media_type):
    raise PackageAlreadyExists("%s - %s - %s exists already " % (package, release, media_type), {
        "package": package,
        "release": release,
        "media_type": media_type})
