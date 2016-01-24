from logtacts.settings import *


SANDSTORM = True

DEBUG = True

SECRET_KEY = get_env_variable("LOGTACTS_SECRET_KEY")

STATIC_URL = '//logtacts.s3.amazonaws.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
)

ADMINS = ()
MANAGERS = ADMINS

ALLOWED_HOSTS = ['*']

EMAIL_HOST=None