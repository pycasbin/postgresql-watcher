from typing import Optional, Callable
from psycopg2 import connect, extensions
from multiprocessing import Process, Pipe
import time
from select import select


POSTGRESQL_CHANNEL_NAME = "casbin_role_watcher"


def casbin_subscription(
    process_conn: Pipe,
    host: str,
    user: str,
    password: str,
    port: Optional[int] = 5432,
    dbname: Optional[str] = "postgres",
    delay: Optional[int] = 2,
    channel_name: Optional[str] = POSTGRESQL_CHANNEL_NAME,
):
    # delay connecting to postgresql (postgresql connection failure)
    time.sleep(delay)
    conn = connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )
    # Can only receive notifications when not in transaction, set this for easier usage
    conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()
    curs.execute(f"LISTEN {channel_name};")
    print("Waiting for casbin policy update")
    while True and not curs.closed:
        if not select([conn], [], [], 5) == ([], [], []):
            print("Casbin policy update identified..")
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                print(f"Notify: {notify.payload}")
                process_conn.send(notify.payload)


class PostgresqlWatcher(object):
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        port: Optional[int] = 5432,
        dbname: Optional[str] = "postgres",
        channel_name: Optional[str] = POSTGRESQL_CHANNEL_NAME,
        start_process: Optional[bool] = True,
    ):
        self.update_callback = None
        self.parent_conn = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.channel_name = channel_name
        self.subscribed_process = self.create_subscriber_process(start_process)

    def create_subscriber_process(
        self,
        start_process: Optional[bool] = True,
        delay: Optional[int] = 2,
    ):
        parent_conn, child_conn = Pipe()
        if not self.parent_conn:
            self.parent_conn = parent_conn
        p = Process(
            target=casbin_subscription,
            args=(
                child_conn,
                self.host,
                self.user,
                self.password,
                self.port,
                self.dbname,
                delay,
                self.channel_name,
            ),
            daemon=True,
        )
        if start_process:
            p.start()
        return p

    def set_update_callback(self, fn_name: Callable):
        print("runtime is set update callback", fn_name)
        self.update_callback = fn_name

    def update(self):
        conn = connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
        )
        # Can only receive notifications when not in transaction, set this for easier usage
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()
        curs.execute(
            f"NOTIFY {self.channel_name},'casbin policy update at {time.time()}'"
        )
        conn.close()
        return True

    def should_reload(self):
        try:
            if self.parent_conn.poll(None):
                message = self.parent_conn.recv()
                print(f"message:{message}")
                return True
        except EOFError:
            print(
                "Child casbin-watcher subscribe process has stopped, "
                "attempting to recreate the process in 10 seconds..."
            )
            self.subscribed_process, self.parent_conn = self.create_subscriber_process(
                delay=10
            )
            return False
