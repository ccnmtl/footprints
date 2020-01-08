import sys

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
