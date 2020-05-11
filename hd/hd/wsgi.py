"""
WSGI config for hd project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
import sys

sys.path.insert(0, PROJECT_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hd.settings")

application = get_wsgi_application()
