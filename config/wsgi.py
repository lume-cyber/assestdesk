import os
from django.core.wsgi import get_wsgi_application
from config.hosting import load_hosting_environment
load_hosting_environment()
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
application = get_wsgi_application()
