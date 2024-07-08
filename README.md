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

```python
from flask_authz import CasbinEnforcer
from postgresql_watcher import PostgresqlWatcher
from flask import Flask
from casbin.persist.adapters import FileAdapter

casbin_enforcer = CasbinEnforcer(app, adapter)
watcher = PostgresqlWatcher(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname=DBNAME)
watcher.set_update_callback(casbin_enforcer.adapter.load_policy)
casbin_enforcer.set_watcher(watcher)

# Call should_reload before every call of enforce to make sure
# the policy is update to date
watcher.should_reload()
if casbin_enforcer.enforce("alice", "data1", "read"):
    # permit alice to read data1
    pass
else:
    # deny the request, show an error
    pass
```

alternatively, if you need more control

```python
from flask_authz import CasbinEnforcer
from postgresql_watcher import PostgresqlWatcher
from flask import Flask
from casbin.persist.adapters import FileAdapter

casbin_enforcer = CasbinEnforcer(app, adapter)
watcher = PostgresqlWatcher(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname=DBNAME)
casbin_enforcer.set_watcher(watcher)

# Call should_reload before every call of enforce to make sure
# the policy is update to date
if watcher.should_reload():
    adapter.load_policy()

if casbin_enforcer.enforce("alice", "data1", "read"):
    # permit alice to read data1
    pass
else:
    # deny the request, show an error
    pass
```

## Basic Usage Example With SSL Enabled

See [PostgresQL documentation](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS) for full details of SSL parameters.

```python
...
watcher = PostgresqlWatcher(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname=DBNAME, sslmode="verify_full", sslcert=SSLCERT, sslrootcert=SSLROOTCERT, sslkey=SSLKEY)
...
```
