"""
WSGI config for bumerang project.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bumerang.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'Settings')

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from configurations.wsgi import get_wsgi_application
application = get_wsgi_application()
