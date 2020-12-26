# postgresql-watcher


Casbin role watcher to be used for monitoring updates to casbin policies
## Installation
```bash
pip install casbin_postgresql_watcher
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


### With django-casbin
> example directory 
 
```python
# postgresql-watcher/examples/django_examples/casbin_middleware/middlewate.py
from postgresql_watcher import PostgresqlWatcher

class CasbinMiddleware:
    """
    Casbin middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize the Casbin enforcer, executed only on once.
        self.enforcer = casbin.Enforcer("casbin_middleware/authz_model.conf", "casbin_middleware/authz_policy.csv")
        # look this , set yourself watcher and watcher_update_callback
        self.enforcer.watcher = PostgresqlWatcher(host=HOST, port=PORT, user=USER, password=PASSWORD)
        self.enforcer.watcher.set_update_callback(self.enforcer.load_policy)
```
Put watcher in `__call__` of CasbinMiddleware to show the watcher functionality more conveniently 
> Please note that the following is for demonstration purposes only and the production environment is not available. Please set up the Watcher to suit your own needs
```python
# postgresql-watcher/examples/django_examples/casbin_middleware/middlewate.py

class CasbinMiddleware:
    """
    Casbin middleware.
    """

    ...

    def __call__(self, request):
        # Check the permission for each request.
        if not self.check_permission(request):
            # Not authorized, return HTTP 403 error.
            self.require_permission()

        # Permission passed, go to next module.
        # look this, Watcher and update_callback are called automatically when the  save policy is executed is executed
        self.enforcer.save_policy()
        response = self.get_response(request)
        return response
```
