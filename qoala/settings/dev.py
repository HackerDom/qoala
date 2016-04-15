"""
This is an example settings/test.py file.
Use this settings file when running tests.
These settings overrides what's in settings/common.py
"""

from .common import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(DATA_DIR, "dev-db.sqlite3"),
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

# Salt for generating tasks patterns

TASK_SALT = "asdkajdlkasjdlkajsdlkajlskdjalksdjkl"

SECRET_KEY = '_=r3oogn=z&!9m!e2l7-f(zz+y7#-+f$3b$e4rku+9&=6z!4ra'

DEBUG = True
TEMPLATE_DEBUG = True
DEV = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )

BROKER_URL = 'django://'
CELERY_ALWAYS_EAGER = True
INSTALLED_APPS += ('kombu.transport.django', )
