# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/footprints/footprints/footprints/templates",
)

MEDIA_ROOT = '/var/www/footprints/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/footprints/footprints/sitemedia'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'footprints',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/footprints/footprints/media/"
DEBUG = False
TEMPLATE_DEBUG = DEBUG

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')				

try:
    from local_settings import *
except ImportError:
    pass
