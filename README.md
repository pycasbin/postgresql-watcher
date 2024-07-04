# postgresql-watcher

[![Build Status](https://github.com/pycasbin/postgresql-watcher/actions/workflows/release.yml/badge.svg)](https://github.com/pycasbin/postgresql-watcher/actions/workflows/release.yml)
[![Coverage Status](https://coveralls.io/repos/github/pycasbin/postgresql-watcher/badge.svg)](https://coveralls.io/github/pycasbin/postgresql-watcher)
[![Version](https://img.shields.io/pypi/v/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![Pyversions](https://img.shields.io/pypi/pyversions/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![Download](https://img.shields.io/pypi/dm/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![Discord](https://img.shields.io/discord/1022748306096537660?logo=discord&label=discord&color=5865F2)](https://discord.gg/S5UjpzGZjN)

Casbin watcher based on PostgreSQL for monitoring updates to casbin policies.

## Installation
```bash
pip install casbin-postgresql-watcher
```

## Basic Usage Example
### With Flask-authz
```python
from flask_authz import CasbinEnforcer
from postgresql_watcher import PostgresqlWatcher
from flask import Flask
from casbin.persist.adapters import FileAdapter

casbin_enforcer = CasbinEnforcer(app, adapter)
watcher = PostgresqlWatcher(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname=DBNAME)
watcher.set_update_callback(casbin_enforcer.e.load_policy)
casbin_enforcer.set_watcher(watcher)
```

## Basic Usage Example With SSL Enabled

See [PostgresQL documentation](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS) for full details of SSL parameters.

### With Flask-authz
```python
from flask_authz import CasbinEnforcer
from postgresql_watcher import PostgresqlWatcher
from flask import Flask
from casbin.persist.adapters import FileAdapter

casbin_enforcer = CasbinEnforcer(app, adapter)
watcher = PostgresqlWatcher(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname=DBNAME, sslmode="verify_full", sslcert=SSLCERT, sslrootcert=SSLROOTCERT, sslkey=SSLKEY)
watcher.set_update_callback(casbin_enforcer.e.load_policy)
casbin_enforcer.set_watcher(watcher)
```


## Django setup with casbin django orm adaptor

Enforcer and Watcher setup
```
# settings.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS += [
    'casbin_adapter.apps.CasbinAdapterConfig',
]

CASBIN_MODEL = os.path.join(BASE_DIR, 'casbin.conf')

from postgresql_watcher.watcher import PostgresqlWatcher
from casbin_adapter.enforcer import enforcer

watcher = PostgresqlWatcher(host=BANK_CONNECT_APIS_PG_HOST_URL, port=BANK_CONNECT_APIS_PG_PORT,
            user=BANK_CONNECT_APIS_PG_USER, password=BANK_CONNECT_APIS_PG_PASSWORD, dbname=BANK_CONNECT_APIS_PG_DBNAME)

def update_enforcer():
    print("before loading policy", enforcer)
    enforcer.load_policy()

watcher.set_update_callback(update_enforcer)
CASBIN_WATCHER = watcher
```

Usage of enforcer

```
#views.py or any other file
from casbin_adapter.enforcer import enforcer

roles = enforcer.get_filtered_named_grouping_policy("g", 1, str(member_id))
```

### Reload Casbin enforcer
In current setup enforcer does not automatically refresh in memory data, whenever required call
```
from setting import watcher 
watcher.should_reload()
```
If there are any changes in db this call will refresh in memory data from database

For automatic reloading of data parent process need to poll child process for messages and call should_reload function if find any message in pipe between child and parent process

