"""
WSGI config for o2m project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "o2m.settings")

from o2m import setup_initial_database
setup_initial_database()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
