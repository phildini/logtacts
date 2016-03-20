from logtacts.settings import *
import dj_database_url

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES['default'] = dj_database_url.parse(get_env_variable('LOGTACTS_DB_URL'))

SECRET_KEY = get_env_variable("LOGTACTS_SECRET_KEY")

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.pebble.ink',
    '.logtacts.com',
    '.contactotter.com',
    '.herokuapp.com',
]

# SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

STATIC_URL = '//logtacts.s3.amazonaws.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
    'opbeat.contrib.django',
)

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
) + MIDDLEWARE_CLASSES

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': get_env_variable('BONSAI_URL'),
        'INDEX_NAME': 'contactotter',
    },
}

OPBEAT = {
    'ORGANIZATION_ID': get_env_variable("OPBEAT_ORG_ID"),
    'APP_ID': get_env_variable("OPBEAT_APP_ID"),
    'SECRET_TOKEN': get_env_variable("OPBEAT_SECRET_KEY"),
}
