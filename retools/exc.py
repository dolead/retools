"""retools exceptions"""


class RetoolsException(Exception):
    """retools package base exception

    Inherits Exception, not BaseException: these are ordinary
    failures callers are meant to catch. Deriving them from
    BaseException made them slip through every `except Exception`
    in their path, taking the process down instead of the call.
    """


class ConfigurationError(RetoolsException):
    """Raised for general configuration errors"""


class CacheConfigurationError(RetoolsException):
    """Raised when there's a cache configuration error"""


class QueueError(RetoolsException):
    """Raised when there's an error in the queue code"""


class AbortJob(RetoolsException):
    """Raised to abort execution of a job"""
