"""
WSGI config for gateway project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from .health_check import health_check


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gateway.settings")
application = get_wsgi_application()
application = health_check(application, '/health/')
