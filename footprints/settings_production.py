from django.conf import settings
from ctlsettings.production import common, init_sentry

from footprints.settings_shared import *  # noqa F403


locals().update(
    common(
        project=project,  # noqa F405
        base=base,  # noqa F405
        INSTALLED_APPS=INSTALLED_APPS,  # noqa F405
        STATIC_ROOT=STATIC_ROOT,  # noqa F405
        s3prefix='ccnmtl',
    ))


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'footprints',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}


try:
    from footprints.local_settings import *  # noqa F403 F405
except ImportError:
    pass


if hasattr(settings, 'SENTRY_DSN'):
    init_sentry(SENTRY_DSN)  # noqa F405
