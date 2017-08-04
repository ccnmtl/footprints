# flake8: noqa
# Django settings for footprints project.
import platform
import os.path
import sys
import djcelery
from ccnmtlsettings.shared import common

project = 'footprints'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

if platform.linux_distribution()[1] == '16.04':
    # 15.04 and later need this set, but it breaks
    # on trusty.
    # yeah, it's not really going to work on non-Ubuntu
    # systems either, but I don't know a good way to
    # check for the specific issue. Anyone not running
    # ubuntu will just need to set this to the
    # appropriate value in their local_settings.py
    SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'footprints',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '',
        'ATOMIC_REQUESTS': True,
    }
}

if ('test' in sys.argv or 'jenkins' in sys.argv or 'validate' in sys.argv
        or 'check' in sys.argv):
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.spatialite',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
            'ATOMIC_REQUESTS': True,
        }
    }


# This setting enables a simple search backend for the Haystack layer
# The simple backend using very basic matching via the database itself.
# It's not recommended for production use but it will return results.
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 15

PROJECT_APPS = [
    'footprints.main',
    'footprints.batch',
    'viaf',
]

USE_TZ = True

TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'django.template.context_processors.csrf')
TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'footprints.main.utils.permissions')
TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'footprints.main.views.django_settings')

MIDDLEWARE_CLASSES += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    'reversion.middleware.RevisionMiddleware'
]

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'bootstrapform',
    'infranil',
    'django_extensions',
    'haystack',
    'footprints.main',
    'rest_framework',
    'reversion',
    'djcelery',
    'celery_haystack',
    'footprints.batch',
    's3sign',
    'registration',
    'django.contrib.gis'
]

djcelery.setup_loader()
BROKER_URL = "amqp://guest:guest@localhost:5672//footprints"
CELERYD_CONCURRENCY = 2

CONTACT_US_EMAIL = 'footprints@columbia.edu'

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = '/'

ACCOUNT_ACTIVATION_DAYS = 7

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'footprints.main.utils.BrowsableAPIRendererNoForms'
    ),
    'PAGINATE_BY': 15,
    'DATETIME_FORMAT': '%m/%d/%y %I:%M %p'
}

if 'test' in sys.argv or 'jenkins' in sys.argv:
    CELERY_ALWAYS_EAGER = True
    BROKER_BACKEND = 'memory'
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    }
    MEDIA_ROOT = './'
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

GOOGLE_MAPS_REVERSE_GEOCODE = \
    'https://maps.googleapis.com/maps/api/geocode/json?address={},{}'

AWS_STORAGE_BUCKET_NAME = "ccnmtl-footprints-static-dev"
MEDIA_URL = 'https://%s.s3.amazonaws.com/uploads/' % AWS_STORAGE_BUCKET_NAME
IMPERSONATE_REQUIRE_SUPERUSER = True

WIND_AFFIL_HANDLERS = [
    'djangowind.auth.StaffMapper',
    'djangowind.auth.SuperuserMapper',
]

ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
REGISTRATION_AUTO_LOGIN = False  # Do not automatically log the user in.
