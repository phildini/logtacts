from logtacts.settings import *
import dj_database_url

DEBUG = True
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

STATIC_URL = '//logtacts.s3.amazonaws.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
)