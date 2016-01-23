# flake8: noqa
# Django settings for footprints project.
import os.path
import sys
from ccnmtlsettings.shared import common

project = 'footprints'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:8080/solr/footprints',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': False,
        'BATCH_SIZE': 10,
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 15

PROJECT_APPS = [
    'footprints.main',
    'viaf'
]

USE_TZ = True

TEMPLATE_CONTEXT_PROCESSORS += [  # noqa
    'django.template.context_processors.csrf',
]

MIDDLEWARE_CLASSES += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    'reversion.middleware.RevisionMiddleware'
]

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'tagging',
    'typogrify',
    'bootstrapform',
    'infranil',
    'django_extensions',
    'haystack',
    'footprints.main',
    'geoposition',
    'rest_framework',
    'reversion',
    'viaf'
]

CONTACT_US_EMAIL = 'footprints@columbia.edu'

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = '/'

ACCOUNT_ACTIVATION_DAYS = 7

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'PAGINATE_BY': 15,
    'DATETIME_FORMAT': '%m/%d/%y %I:%M %p'
}

if 'test' in sys.argv or 'jenkins' in sys.argv:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    }
    MEDIA_ROOT = './'
