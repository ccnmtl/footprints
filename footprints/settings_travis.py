# flake8: noqa
import sys
from footprints.settings_shared import *


try:
    from footprints.local_settings import *
except ImportError:
    pass


if ('test' in sys.argv or 'jenkins' in sys.argv or 'validate' in sys.argv
        or 'check' in sys.argv):
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'test_footprints',
            'HOST': '',
            'PORT': '',
            'USER': 'postgres',
            'PASSWORD': '',
            'ATOMIC_REQUESTS': True,
        }
    }
