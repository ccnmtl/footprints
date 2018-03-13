# flake8: noqa
from footprints.settings_shared import *

try:
    from footprints.local_settings import *
except ImportError:
    pass
