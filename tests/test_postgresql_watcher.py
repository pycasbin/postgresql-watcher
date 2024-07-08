import sys
import unittest
from multiprocessing.connection import Pipe
from time import sleep
import logging

from postgresql_watcher import PostgresqlWatcher
from postgresql_watcher.watcher import CASBIN_CHANNEL_SELECT_TIMEOUT
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

def get_watcher():
    return PostgresqlWatcher(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        dbname=DBNAME,
        logger=logger,
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
        pg_watcher = get_watcher()
        if _winapi:
            assert isinstance(pg_watcher.parent_conn, connection.PipeConnection)
        else:
            assert isinstance(pg_watcher.parent_conn, connection.Connection)
        assert isinstance(pg_watcher.subscribed_process, context.Process)

    def test_update_pg_watcher(self):
        pg_watcher = get_watcher()
        sleep(5) # Wait for casbin_channel_subscription initialization
        pg_watcher.update()
        sleep(CASBIN_CHANNEL_SELECT_TIMEOUT * 2)
        self.assertTrue(pg_watcher.should_reload())

    def test_default_update_callback(self):
        pg_watcher = get_watcher()
        assert pg_watcher.update_callback is None

    def test_add_update_callback(self):
        pg_watcher = get_watcher()
        def _test_callback():
            pass

        pg_watcher.set_update_callback(_test_callback)
        assert pg_watcher.update_callback == _test_callback


if __name__ == "__main__":
    unittest.main()
