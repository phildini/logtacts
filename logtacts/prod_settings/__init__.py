from logtacts.settings import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES['default'] = dj_database_url.parse(get_env_variable('LOGTACTS_DB_URL'))

SECRET_KEY = get_env_variable("LOGTACTS_SECRET_KEY")

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',
    '.pebble.ink',
    '.logtacts.com',
]

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

STATIC_URL = '//logtacts.s3.amazonaws.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
)