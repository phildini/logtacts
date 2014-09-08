from .base import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES['default'] = dj_database_url.config()

SECRET_KEY = get_env_variable("SECRET_KEY")

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',
]

INSTALLED_APPS += (
    'gunicorn',
)