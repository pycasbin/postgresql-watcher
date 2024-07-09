from enum import IntEnum
from logging import Logger
from multiprocessing.connection import Connection
from select import select
from signal import signal, SIGINT, SIGTERM
from time import sleep
from typing import Optional

from psycopg2 import connect, extensions, InterfaceError


CASBIN_CHANNEL_SELECT_TIMEOUT = 1  # seconds


def casbin_channel_subscription(
    process_conn: Connection,
    logger: Logger,
    host: str,
    user: str,
    password: str,
    channel_name: str,
    port: int = 5432,
    dbname: str = "postgres",
    delay: int = 2,
    sslmode: Optional[str] = None,
    sslrootcert: Optional[str] = None,
    sslcert: Optional[str] = None,
    sslkey: Optional[str] = None,
):
    # delay connecting to postgresql (postgresql connection failure)
    sleep(delay)
    db_connection = connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
        sslmode=sslmode,
        sslrootcert=sslrootcert,
        sslcert=sslcert,
        sslkey=sslkey,
    )
    # Can only receive notifications when not in transaction, set this for easier usage
    db_connection.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    db_cursor = db_connection.cursor()
    context_manager = _ConnectionManager(db_connection, db_cursor)

    with context_manager:
        db_cursor.execute(f"LISTEN {channel_name};")
        logger.debug("Waiting for casbin policy update")
        process_conn.send(_ChannelSubscriptionMessage.IS_READY)

        while not db_cursor.closed:
            try:
                select_result = select(
                    [db_connection],
                    [],
                    [],
                    CASBIN_CHANNEL_SELECT_TIMEOUT,
                )
                if select_result != ([], [], []):
                    logger.debug("Casbin policy update identified")
                    db_connection.poll()
                    while db_connection.notifies:
                        notify = db_connection.notifies.pop(0)
                        logger.debug(f"Notify: {notify.payload}")
                        process_conn.send(_ChannelSubscriptionMessage.RECEIVED_UPDATE)
            except (InterfaceError, OSError) as e:
                # Log an exception if these errors occurred without the context beeing closed
                if not context_manager.connections_were_closed:
                    logger.critical(e, exc_info=True)
                break


class _ChannelSubscriptionMessage(IntEnum):
    IS_READY = 1
    RECEIVED_UPDATE = 2


class _ConnectionManager:
    """
    You can not use 'with' and a connection / cursor directly in this setup.
    For more details see this issue: https://github.com/psycopg/psycopg2/issues/941#issuecomment-864025101.
    As a workaround this connection manager / context manager class is used, that also handles SIGINT and SIGTERM and
    closes the database connection.
    """

    def __init__(self, connection, cursor) -> None:
        self.connection = connection
        self.cursor = cursor
        self.connections_were_closed = False

    def __enter__(self):
        signal(SIGINT, self._close_connections)
        signal(SIGTERM, self._close_connections)
        return self

    def _close_connections(self, *_):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.connections_were_closed = True

    def __exit__(self, *_):
        self._close_connections()
