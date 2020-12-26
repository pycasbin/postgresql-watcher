from typing import Optional, Any
from psycopg2 import connect, extensions
from multiprocessing import Process, Pipe
import time
from select import select
from abc import ABC
from abc import abstractmethod
POSTGRESQL_CHANNEL_NAME = "casbin_role_watcher"


class Watcher(ABC):
    """
    Watcher interface as it should be implemented for flask-casbin
    """

    @abstractmethod
    def update(self):
        """
        Watcher interface as it should be implemented for flask-casbin
        Returns:
            None
        """
        pass

    @abstractmethod
    def set_update_callback(self):
        """
        Set the update callback to be used when an update is detected
        Returns:
            None
        """
        pass

    @abstractmethod
    def should_reload(self):
        """
        Method which checks if there is an update necessary for the casbin
        roles. This is called with each flask request.
        Returns:
            Bool
        """
        pass


def casbin_subscription(
    process_conn:Any,
    host: str,
    user: str,
    password: str,
    port: Optional[int] = 5432,
    delay: Optional[int] = 2,
    channel_name: Optional[str] = POSTGRESQL_CHANNEL_NAME,
):
    # delay connecting to postgresql (postgresql connection failure)
    time.sleep(delay)
    conn = connect(host=host, port=port, user=user, password=password)
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




class PostgresqlWatcher(object):
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        port: Optional[int] = 5432,
        channel_name: Optional[str] = POSTGRESQL_CHANNEL_NAME,
        start_process: Optional[bool] = True,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.channel_name = channel_name
        self.subscribed_process, self.parent_conn = self.create_subscriber_process(
            start_process
        )

    def create_subscriber_process(
        self,
        start_process: Optional[bool] = True,
        delay: Optional[int] = 2,
    ):
        parent_conn, child_conn = Pipe()
        p = Process(
            target=casbin_subscription,
            args=(
                child_conn,
                self.host,
                self.user,
                self.password,
                self.port,
                delay,
                self.channel_name,
            ),
            daemon=True,
        )
        if start_process:
            p.start()
        return p, parent_conn

    def update_callback(self):
        print("callback called because casbin role updated")

    def set_update_callback(self, fn_name: Any):
        print("runtime is set update callback",fn_name)
        self.update_callback = fn_name


    def update(self):
        conn = connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
        )
        # Can only receive notifications when not in transaction, set this for easier usage
        print("watcher is run")
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        curs = conn.cursor()
        curs.execute(
            f"NOTIFY {self.channel_name},'casbin policy update at {time.time()}'"
        )
        conn.close()
        self.update_callback()
        return True

    def should_reload(self):
        try:
            if self.parent_conn.poll():
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