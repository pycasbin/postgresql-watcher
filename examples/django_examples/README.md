# django-casbin

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/casbin/lobby)

django-casbin is an authorization middleware for [Django](https://www.djangoproject.com/), it's based on [PyCasbin](https://github.com/casbin/pycasbin).

## Installation

```
pip install casbin
```

## Simple Example

This repo is just a working Django app that shows the usage of django-casbin. To use it in your existing Django app, you need:

- Add the middleware to your Django app's ``settings.py``:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'casbin_middleware.middleware.CasbinMiddleware', # Add this line, must after AuthenticationMiddleware.
]
```

- Copy ``casbin_middleware`` folder to your Django's top folder, modify ``casbin_middleware/middleware.py`` if you need:

```python
import casbin

    def __init__(self, get_response):
        self.get_response = get_response
        # load the casbin model and policy from files.
        # change the 2nd arg to use a database.
        self.enforcer = casbin.Enforcer("casbin_middleware/authz_model.conf", "casbin_middleware/authz_policy.csv")

    def check_permission(self, request):
        # change the user, path, method as you need.
        user = request.user.username
        if request.user.is_anonymous:
            user = 'anonymous'
        path = request.path
        method = request.method
        return self.enforcer.enforce(user, path, method)
```

- The default policy ``authz_policy.csv`` is:

```csv
p, anonymous, /, GET
p, admin, *, *
g, alice, admin
```

It means ``anonymous`` user can only access homepage ``/``. Admin users like alice can access any pages. Currently all accesses are regarded as ``anonymous``. Add your authentication to let a user log in.

## Documentation

The authorization determines a request based on ``{subject, object, action}``, which means what ``subject`` can perform what ``action`` on what ``object``. In this plugin, the meanings are:

1. ``subject``: the logged-in user name
2. ``object``: the URL path for the web resource like "dataset1/item1"
3. ``action``: HTTP method like GET, POST, PUT, DELETE, or the high-level actions you defined like "read-file", "write-blog"

For how to write authorization policy and other details, please refer to [the Casbin's documentation](https://casbin.org).

## Getting Help

- [Casbin](https://casbin.org)

## License

This project is under Apache 2.0 License. See the [LICENSE](LICENSE) file for the full license text.
