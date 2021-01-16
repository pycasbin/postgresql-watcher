# postgresql-watcher


Casbin role watcher to be used for monitoring updates to casbin policies
## Installation
```bash
pip install postgresql-watcher
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