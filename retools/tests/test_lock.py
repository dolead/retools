import time
import unittest
from unittest.mock import Mock, patch

import pytest
import redis


class TestLock(unittest.TestCase):
    def _makeOne(self):
        from retools.lock import Lock

        return Lock

    def _lockException(self):
        from retools.lock import LockTimeout

        return LockTimeout

    def test_redis_sub(self):
        mock_redis = Mock(spec=redis.Redis)
        import retools

        old_conn = retools.global_connection.redis
        try:
            retools.global_connection.redis = mock_redis

            def test_it():
                lock = self._makeOne()
                with lock("somekey"):
                    pass  # the critical section

            test_it()
            method_names = [x[0] for x in mock_redis.method_calls]
            assert method_names[0] == "setnx"
            assert method_names[1] == "expire"
            assert method_names[2] == "delete"
            assert len(method_names) == 3
        finally:
            retools.global_connection.redis = old_conn

    def test_nocontention(self):
        mock_redis = Mock(spec=redis.Redis)

        @patch("retools.global_connection._redis", mock_redis)
        def test_it():
            lock = self._makeOne()
            with lock("somekey"):
                pass  # the critical section

        test_it()
        method_names = [x[0] for x in mock_redis.method_calls]
        assert method_names[0] == "setnx"
        assert method_names[1] == "expire"
        assert method_names[2] == "delete"
        assert len(method_names) == 3

    def test_nocontention_and_no_lock_delete(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_time = Mock()
        vals = [35, 0, 0, 0]
        mock_time.side_effect = vals.pop

        @patch("retools.global_connection._redis", mock_redis)
        @patch("time.time", mock_time)
        def test_it():
            lock = self._makeOne()
            with lock("somekey", expires=30):
                pass  # the critical section

        test_it()
        method_names = [x[0] for x in mock_redis.method_calls]
        assert method_names[0] == "setnx"
        assert "delete" not in method_names

    def test_contention_and_someone_else_replacing_timeout(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_time = Mock()
        vals = [35, 0, 0, 0]
        mock_time.side_effect = vals.pop
        mock_redis.get.return_value = False
        mock_redis.setnx.return_value = False
        timeout = self._lockException()

        @patch("retools.global_connection._redis", mock_redis)
        @patch("time.time", mock_time)
        @patch("time.sleep", Mock())
        def test_it():
            lock = self._makeOne()
            with lock("somekey", expires=30, timeout=0):  # pragma: nocover
                pass  # the critical section

        with pytest.raises(timeout):
            test_it()
        method_names = [x[0] for x in mock_redis.method_calls]
        assert method_names[0] == "setnx"
        assert len(method_names) == 2

    def test_contention(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_redis.get.return_value = 150
        mock_redis.getset.return_value = 150
        mock_redis.setnx.return_value = False

        @patch("retools.global_connection._redis", mock_redis)
        def test_it():
            lock = self._makeOne()
            with lock("somekey"):
                pass  # the critical section

        test_it()
        assert len(mock_redis.method_calls) == 5
        setnx, get = mock_redis.method_calls[:2]
        assert setnx[1][0] == "somekey"
        assert get[1][0] == "somekey"

    def test_timeout_current_val_is_newer(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_redis.setnx.return_value = False
        mock_redis.get.return_value = time.time() + 200
        timeout = self._lockException()
        mock_time = Mock()
        mock_time.return_value = 0

        array = []

        @patch("retools.global_connection._redis", mock_redis)
        @patch("time.sleep", mock_time)
        def test_it():
            lock = self._makeOne()
            with lock("somekey", timeout=1):
                array.append(4)  # pragma: nocover

        with pytest.raises(timeout):
            test_it()
        assert len(array) == 0

    def test_timeout_no_current_value_and_mock_redis(self):
        mock_redis = Mock(spec=redis.Redis)
        mock_redis.setnx.return_value = False
        mock_redis.get.return_value = 150
        mock_redis.getset.return_value = False
        timeout = self._lockException()
        mock_time = Mock()
        mock_time.return_value = 0

        array = []

        @patch("retools.global_connection._redis", mock_redis)
        @patch("time.sleep", mock_time)
        def test_it():
            lock = self._makeOne()
            with lock("somekey", timeout=1, redis=mock_redis):
                array.append(4)  # pragma: nocover

        with pytest.raises(timeout):
            test_it()
        assert len(array) == 0
