# postgresql-watcher

[![tests](https://github.com/pycasbin/postgresql-watcher/actions/workflows/release.yml/badge.svg)](https://github.com/pycasbin/postgresql-watcher/actions/workflows/release.yml)
[![Coverage Status](https://coveralls.io/repos/github/pycasbin/postgresql-watcher/badge.svg)](https://coveralls.io/github/pycasbin/postgresql-watcher)
[![Version](https://img.shields.io/pypi/v/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![Download](https://img.shields.io/pypi/dm/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![Discord](https://img.shields.io/discord/1022748306096537660?logo=discord&label=discord&color=5865F2)](https://discord.gg/S5UjpzGZjN)

Casbin role watcher to be used for monitoring updates to casbin policies
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
