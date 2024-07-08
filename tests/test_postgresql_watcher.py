import sys
import unittest
from unittest.mock import MagicMock
from multiprocessing.connection import Pipe
from time import sleep
import logging

from postgresql_watcher import PostgresqlWatcher
from postgresql_watcher.casbin_channel_subscription import CASBIN_CHANNEL_SELECT_TIMEOUT
from multiprocessing import connection, context

# Warning!!! , Please setup yourself config
HOST = "127.0.0.1"
PORT = 5432
USER = "postgres"
PASSWORD = "123456"
DBNAME = "postgres"

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def get_watcher(channel_name):
    return PostgresqlWatcher(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        dbname=DBNAME,
        logger=logger,
        channel_name=channel_name,
    )


try:
    import _winapi
    from _winapi import WAIT_OBJECT_0, WAIT_ABANDONED_0, WAIT_TIMEOUT, INFINITE
except ImportError as e:
    if sys.platform == "win32":
        raise e
    _winapi = None


class TestConfig(unittest.TestCase):
    def test_pg_watcher_init(self):
        pg_watcher = get_watcher("test_pg_watcher_init")
        if _winapi:
            assert isinstance(pg_watcher.parent_conn, connection.PipeConnection)
        else:
            assert isinstance(pg_watcher.parent_conn, connection.Connection)
        assert isinstance(pg_watcher.subscription_proces, context.Process)

    def test_update_single_pg_watcher(self):
        pg_watcher = get_watcher("test_update_single_pg_watcher")
        pg_watcher.update()
        sleep(CASBIN_CHANNEL_SELECT_TIMEOUT * 2)
        self.assertTrue(pg_watcher.should_reload())

    def test_no_update_single_pg_watcher(self):
        pg_watcher = get_watcher("test_no_update_single_pg_watcher")
        sleep(CASBIN_CHANNEL_SELECT_TIMEOUT * 2)
        self.assertFalse(pg_watcher.should_reload())

    def test_update_mutiple_pg_watcher(self):
        channel_name = "test_update_mutiple_pg_watcher"
        main_watcher = get_watcher(channel_name)

        other_watchers = [get_watcher(channel_name) for _ in range(5)]
        main_watcher.update()
        sleep(CASBIN_CHANNEL_SELECT_TIMEOUT * 2)
        for watcher in other_watchers:
            self.assertTrue(watcher.should_reload())

    def test_no_update_mutiple_pg_watcher(self):
        channel_name = "test_no_update_mutiple_pg_watcher"
        main_watcher = get_watcher(channel_name)

        other_watchers = [get_watcher(channel_name) for _ in range(5)]
        sleep(CASBIN_CHANNEL_SELECT_TIMEOUT * 2)
        for watcher in other_watchers:
            self.assertFalse(watcher.should_reload())
        self.assertFalse(main_watcher.should_reload())

    def test_update_handler_called(self):
        channel_name = "test_update_handler_called"
        main_watcher = get_watcher(channel_name)
        handler = MagicMock()
        main_watcher.set_update_callback(handler)
        main_watcher.update()
        sleep(CASBIN_CHANNEL_SELECT_TIMEOUT * 2)
        self.assertTrue(main_watcher.should_reload())
        self.assertTrue(handler.call_count == 1)

    def test_update_handler_not_called(self):
        channel_name = "test_update_handler_not_called"
        main_watcher = get_watcher(channel_name)
        handler = MagicMock()
        main_watcher.set_update_callback(handler)
        sleep(CASBIN_CHANNEL_SELECT_TIMEOUT * 2)
        self.assertFalse(main_watcher.should_reload())
        self.assertTrue(handler.call_count == 0)


if __name__ == "__main__":
    unittest.main()
