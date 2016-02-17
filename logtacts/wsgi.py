"""
WSGI config for logtacts project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import newrelic.agent
import os

newrelic.agent.initialize('/home/deploy/logtacts/newrelic.ini')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logtacts.prod_settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
application = newrelic.agent.wsgi_application()(application)
