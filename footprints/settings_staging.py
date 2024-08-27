from django.conf import settings
from footprints.settings_shared import *  # noqa F403
from ctlsettings.staging import common, init_sentry


locals().update(
    common(
        project=project,  # noqa F405
        base=base,  # noqa F405
        STATIC_ROOT=STATIC_ROOT,  # noqa F405
        INSTALLED_APPS=INSTALLED_APPS,  # noqa F405
        s3prefix='ccnmtl',
    ))


try:
    from footprints.local_settings import *  # noqa F403 F405
except ImportError:
    pass


if hasattr(settings, 'SENTRY_DSN'):
    init_sentry(SENTRY_DSN)  # noqa F405
