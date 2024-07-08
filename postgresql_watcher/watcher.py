from typing import Optional, Callable
from psycopg2 import connect, extensions
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import time
from select import select
from logging import Logger, getLogger
from .casbin_channel_subscription import (
    casbin_channel_subscription,
    _ChannelSubscriptionMessage,
)


POSTGRESQL_CHANNEL_NAME = "casbin_role_watcher"


class PostgresqlWatcher(object):

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        port: int = 5432,
        dbname: str = "postgres",
        channel_name: Optional[str] = None,
        start_listening: bool = True,
        sslmode: Optional[str] = None,
        sslrootcert: Optional[str] = None,
        sslcert: Optional[str] = None,
        sslkey: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        Initialize a PostgresqlWatcher object.

        Args:
            host (str): Hostname of the PostgreSQL server.
            user (str): PostgreSQL username.
            password (str): Password for the user.
            port (int): Post of the PostgreSQL server. Defaults to 5432.
            dbname (str): Database name. Defaults to "postgres".
            channel_name (str): The name of the channel to listen to and to send updates to. When None a default is used.
            start_listening (bool, optional): Flag whether to start listening to updates on the PostgreSQL channel. Defaults to True.
            sslmode (Optional[str], optional): See `psycopg2.connect` for details. Defaults to None.
            sslrootcert (Optional[str], optional): See `psycopg2.connect` for details. Defaults to None.
            sslcert (Optional[str], optional): See `psycopg2.connect` for details. Defaults to None.
            sslkey (Optional[str], optional): See `psycopg2.connect` for details. Defaults to None.
            logger (Optional[Logger], optional): Custom logger to use. Defaults to None.
        """
        self.update_callback = None
        self.parent_conn = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.channel_name = (
            channel_name if channel_name is not None else POSTGRESQL_CHANNEL_NAME
        )
        self.sslmode = sslmode
        self.sslrootcert = sslrootcert
        self.sslcert = sslcert
        self.sslkey = sslkey
        if logger is None:
            logger = getLogger()
        self.logger = logger
        self.parent_conn: Connection | None = None
        self.child_conn: Connection | None = None
        self.subscription_process: Process | None = None
        self._create_subscription_process(start_listening)
        self.update_callback: Optional[Callable[[None], None]] = None

    def __del__(self) -> None:
        self._cleanup_connections_and_processes()

    def _create_subscription_process(
        self,
        start_listening=True,
        delay: Optional[int] = 2,
    ) -> None:
        self._cleanup_connections_and_processes()

        self.parent_conn, self.child_conn = Pipe()
        self.subscription_proces = Process(
            target=casbin_channel_subscription,
            args=(
                self.child_conn,
                self.logger,
                self.host,
                self.user,
                self.password,
                self.channel_name,
                self.port,
                self.dbname,
                delay,
                self.sslmode,
                self.sslrootcert,
                self.sslcert,
                self.sslkey,
            ),
            daemon=True,
        )
        if start_listening:
            self.start()

    def start(self):
        if not self.subscription_proces.is_alive():
            # Start listening to messages
            self.subscription_proces.start()
            # And wait for the Process to be ready to listen for updates
            # from PostgreSQL
            while True:
                if self.parent_conn.poll():
                    message = int(self.parent_conn.recv())
                    if message == _ChannelSubscriptionMessage.IS_READY:
                        break
                time.sleep(1 / 1000)  # wait for 1 ms

    def _cleanup_connections_and_processes(self) -> None:
        # Clean up potentially existing Connections and Processes
        if self.parent_conn is not None:
            self.parent_conn.close()
            self.parent_conn = None
        if self.child_conn is not None:
            self.child_conn.close()
            self.child_conn = None
        if self.subscription_process is not None:
            self.subscription_process.terminate()
            self.subscription_process = None

    def set_update_callback(self, update_handler: Optional[Callable[[None], None]]):
        """
        Set the handler called, when the Watcher detects an update.
        Recommendation: `casbin_enforcer.adapter.load_policy`
        """
        self.update_callback = update_handler

    def update(self) -> None:
        """
        Called by `casbin.Enforcer` when an update to the model was made.
        Informs other watchers via the PostgreSQL channel.
        """
        conn = connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
            sslmode=self.sslmode,
            sslrootcert=self.sslrootcert,
            sslcert=self.sslcert,
            sslkey=self.sslkey,
        )
        # Can only receive notifications when not in transaction, set this for easier usage
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()
        curs.execute(
            f"NOTIFY {self.channel_name},'casbin policy update at {time.time()}'"
        )
        conn.close()

    def should_reload(self) -> bool:
        try:
            if self.parent_conn.poll():
                message = int(self.parent_conn.recv())
                received_update = message == _ChannelSubscriptionMessage.RECEIVED_UPDATE
                if received_update and self.update_callback is not None:
                    self.update_callback()
                return received_update
        except EOFError:
            self.logger.warning(
                "Child casbin-watcher subscribe process has stopped, "
                "attempting to recreate the process in 10 seconds..."
            )
            self._create_subscription_process(delay=10)

        return False
