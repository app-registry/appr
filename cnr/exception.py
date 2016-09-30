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


class InvalidVersion(CnrException):
    status_code = 422
    errorcode = "invalid-version"


class PackageAlreadyExists(CnrException):
    status_code = 409
    errorcode = "package-exists"


class ChannelAlreadyExists(CnrException):
    status_code = 409
    errorcode = "channel-exists"


class PackageNotFound(CnrException):
    status_code = 404
    errorcode = "package-not-found"


class ChannelNotFound(CnrException):
    status_code = 404
    errorcode = "channel-not-found"


class PackageVersionNotFound(CnrException):
    status_code = 404
    errorcode = "package-version-not-found"


class UnauthorizedAccess(CnrException):
    status_code = 401
    errorcode = "unauthorized-access"
