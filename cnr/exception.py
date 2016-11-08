class CnrException(Exception):
    status_code = 500
    errorcode = "internal-error"

    def __init__(self, message, payload=None):
        super(CnrException, self).__init__()
        self.payload = dict(payload or ())
        self.message = message

    def to_dict(self):
        return {"code": self.errorcode,
                "message": self.message,
                "details": self.payload}

    def __str__(self):
        return self.message


class InvalidUsage(CnrException):
    status_code = 400
    errorcode = "invalid-usage"


class InvalidRelease(CnrException):
    status_code = 422
    errorcode = "invalid-release"


class InvalidParams(CnrException):
    status_code = 422
    errorcode = "invalid-parameters"


class PackageAlreadyExists(CnrException):
    status_code = 409
    errorcode = "package-exists"


class PackageNotFound(CnrException):
    status_code = 404
    errorcode = "package-not-found"


class ResourceNotFound(CnrException):
    status_code = 404
    errorcode = "resource-not-found"


class ChannelNotFound(CnrException):
    status_code = 404
    errorcode = "channel-not-found"


class Forbidden(CnrException):
    status_code = 403
    errorcode = "forbidden"


class PackageReleaseNotFound(CnrException):
    status_code = 404
    errorcode = "package-release-not-found"


class UnauthorizedAccess(CnrException):
    status_code = 401
    errorcode = "unauthorized-access"


class Unsupported(CnrException):
    status_code = 501
    errorcode = "unsupported"


class UnableToLockResource(CnrException):
    status_code = 409
    errorcode = "resource-in-use"


def raise_package_not_found(package, release=None, media_type=None):
    raise PackageNotFound("package %s doesn't exist, v: %s, type: %s" % (package, str(release), str(media_type)),
                          {'package': package, 'release': release, 'media_type': media_type})


def raise_channel_not_found(package, channel=None, release=None):
    if channel is None:
        raise ChannelNotFound("No channel found for package '%s'" % (package),
                              {'package': package})
    else:
        raise ChannelNotFound("Channel '%s' doesn't exist for package '%s'" % (channel, package),
                              {'channel': channel, 'package': package, 'release': release})


def raise_package_exists(package, release, media_type):
    raise PackageAlreadyExists("%s - %s - %s exists already " % (package, release, media_type),
                               {"package": package, "release": release, "media_type": media_type})
