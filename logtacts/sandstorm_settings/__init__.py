from logtacts.settings import *


SANDSTORM = True

DEBUG = False

SECRET_KEY = get_env_variable("LOGTACTS_SECRET_KEY")

STATIC_URL = '//logtacts.s3.amazonaws.com/assets/'

INSTALLED_APPS += (
    'gunicorn',
)

ADMINS = ()
MANAGERS = ADMINS

ALLOWED_HOSTS = ['*']

TEMPLATES[0]['OPTIONS']['context_processors'].append('django_sandstorm.context.sandstorm')

INSTALLED_APPS += (
    'django_sandstorm',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)

MIDDLEWARE_CLASSES = (
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_sandstorm.middleware.SandstormMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'logtacts.middleware.TimezoneMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/var/', 'logtacts-sandstorm.sqlite3'),
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join('/var/', 'whoosh_index'),
    },
}