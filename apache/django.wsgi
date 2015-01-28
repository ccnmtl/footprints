import os, sys, site

# enable the virtualenv
site.addsitedir('/var/www/footprints/footprints/ve/lib/python2.7/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/var/www/footprints/footprints/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'footprints.settings_production'

import django.core.handlers.wsgi
import django
django.setup()
application = django.core.handlers.wsgi.WSGIHandler()
