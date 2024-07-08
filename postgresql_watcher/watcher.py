from typing import Optional, Callable
from psycopg2 import connect, extensions
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import time
from select import select
from logging import Logger, getLogger


POSTGRESQL_CHANNEL_NAME = "casbin_role_watcher"


class PostgresqlWatcher(object):

    @staticmethod
    def set_channel_name(channel_name: str) -> None:
        """
        Customize the Postgres channel name. This have to be done before initializing a PostgresqlWatcher object.

        Args:
            channel_name (str): New channel name
        """
        global POSTGRESQL_CHANNEL_NAME
        POSTGRESQL_CHANNEL_NAME = channel_name

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        port: Optional[int] = 5432,
        dbname: Optional[str] = "postgres",
        channel_name: Optional[str] = POSTGRESQL_CHANNEL_NAME,
        start_process: Optional[bool] = True,
        sslmode: Optional[str] = None,
        sslrootcert: Optional[str] = None,
        sslcert: Optional[str] = None,
        sslkey: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        self.update_callback = None
        self.parent_conn = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.channel_name = channel_name
        self.sslmode = sslmode
        self.sslrootcert = sslrootcert
        self.sslcert = sslcert
        self.sslkey = sslkey
        if logger is None:
            logger = getLogger()
        self.logger = logger
        self.parent_conn: Connection = None
        self.child_conn: Connection = None
        self.subscription_process: Process = None
        self._create_subscription_process(start_process)

    def _create_subscription_process(
        self,
        start_process: Optional[bool] = True,
        delay: Optional[int] = 2,
    ) -> None:
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

        self.parent_conn, self.child_conn = Pipe()
        self.subscribed_process = Process(
            target=_casbin_channel_subscription,
            args=(
                self.child_conn,
                self.logger,
                self.host,
                self.user,
                self.password,
                self.port,
                self.dbname,
                delay,
                self.channel_name,
                self.sslmode,
                self.sslrootcert,
                self.sslcert,
                self.sslkey,
            ),
            daemon=True,
        )
        if start_process:
            self.subscribed_process.start()

    def set_update_callback(self, fn_name: Callable):
        self.logger.debug(f"runtime is set update callback {fn_name}")
        self.update_callback = fn_name

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
        return True

    def should_reload(self) -> bool:
        try:
            if self.parent_conn.poll(None):
                message = self.parent_conn.recv()
                self.logger.debug(f"message:{message}")
                return True
        except EOFError:
            self.logger.warning(
                "Child casbin-watcher subscribe process has stopped, "
                "attempting to recreate the process in 10 seconds..."
            )
            self._create_subscription_process(delay=10)

        return False


def _casbin_channel_subscription(
    process_conn: Connection,
    logger: Logger,
    host: str,
    user: str,
    password: str,
    port: Optional[int] = 5432,
    dbname: Optional[str] = "postgres",
    delay: Optional[int] = 2,
    channel_name: Optional[str] = POSTGRESQL_CHANNEL_NAME,
    sslmode: Optional[str] = None,
    sslrootcert: Optional[str] = None,
    sslcert: Optional[str] = None,
    sslkey: Optional[str] = None,
):
    # delay connecting to postgresql (postgresql connection failure)
    time.sleep(delay)
    conn = connect(
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
    conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()
    curs.execute(f"LISTEN {channel_name};")
    logger.debug("Waiting for casbin policy update")
    while True and not curs.closed:
        if not select([conn], [], [], 5) == ([], [], []):
            logger.debug("Casbin policy update identified..")
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                logger.debug(f"Notify: {notify.payload}")
                process_conn.send(notify.payload)
