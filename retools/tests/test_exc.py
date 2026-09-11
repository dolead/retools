import unittest

from retools.exc import (
    AbortJob,
    CacheConfigurationError,
    ConfigurationError,
    QueueError,
    RetoolsException,
)
from retools.lock import LockTimeout


class TestExceptions(unittest.TestCase):
    def test_every_error_is_an_ordinary_exception(self):
        for error_class in (
            RetoolsException,
            ConfigurationError,
            CacheConfigurationError,
            QueueError,
            AbortJob,
            LockTimeout,
        ):
            assert issubclass(error_class, Exception)

    def test_package_errors_share_a_base(self):
        for error_class in (
            ConfigurationError,
            CacheConfigurationError,
            QueueError,
            AbortJob,
        ):
            assert issubclass(error_class, RetoolsException)

    def test_a_bare_except_exception_catches_them(self):
        for error_class in (RetoolsException, LockTimeout):
            try:
                raise error_class("boom")
            except Exception as error:
                assert isinstance(error, error_class)
            else:
                raise AssertionError(
                    f"{error_class.__name__} escaped `except Exception`"
                )
