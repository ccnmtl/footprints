# flake8: noqa
from footprints.settings_shared import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True,
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
BROKER_URL = "amqp://guest:guest@rabbitmq:5672/"

try:
    from footprints.local_settings import *
except ImportError:
    pass
