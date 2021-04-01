# postgresql-watcher

[![tests](https://github.com/pycasbin/postgresql-watcher/actions/workflows/release.yml/badge.svg)](https://github.com/pycasbin/postgresql-watcher/actions/workflows/release.yml)
[![Coverage Status](https://coveralls.io/repos/github/pycasbin/postgresql-watcher/badge.svg)](https://coveralls.io/github/pycasbin/postgresql-watcher)
[![Version](https://img.shields.io/pypi/v/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![Download](https://img.shields.io/pypi/dm/casbin-postgresql-watcher.svg)](https://pypi.org/project/casbin-postgresql-watcher/)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/casbin/lobby)

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
watcher = PostgresqlWatcher(host=HOST, port=PORT, user=USER, password=PASSWORD)
watcher.set_update_callback(casbin_enforcer.e.load_policy())
casbin_enforcer.set_watcher(watcher)
```