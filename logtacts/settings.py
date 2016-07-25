"""
Django settings for logtacts project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import warnings
from django.core.exceptions import ImproperlyConfigured
from unipath import Path


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        if DEBUG:
            warnings.warn(error_msg)
        else:
            raise ImproperlyConfigured(error_msg)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!3yyflcosue5z!d225xmf(4g2blxlu+ac0jzjf+%8wh0t23*=!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SANDSTORM = False

ALLOWED_HOSTS = []

SITE_ID=1

PROJECT_ROOT = Path(BASE_DIR)

MEDIA_ROOT = PROJECT_ROOT.child('media')
STATIC_ROOT = PROJECT_ROOT.child('static').child('dist')
STATICFILES_DIRS = (
    PROJECT_ROOT.child('static'),
)
STATIC_URL = '/static/'

LIST_PAGINATE_BY = 25
LIST_PAGINATE_ORPHANS = 5

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PROJECT_ROOT.child('templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'logtacts.context_processors.donottrack',
            ],
        },
    },
]

# Application definition

INSTALLED_APPS = (
    # Django first-party apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.foursquare',
    'django_gravatar',
    'djangosecure',
    'haystack',
    'rest_framework',
    'rest_framework.authtoken',
    'simple_history',
    'floppyforms',
    'nexus',
    'gargoyle',
    'channels',
    'rest_framework_swagger',
    # ContactOtter Apps
    'contacts.apps.ContactConfig',
    'invitations.apps.InvitationConfig',
    'profiles.apps.ProfilesConfig',
)

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'logtacts.middleware.TimezoneMiddleware',
    'logtacts.middleware.DoNotTrackMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ROOT_URLCONF = 'logtacts.urls'

WSGI_APPLICATION = 'logtacts.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

ADMINS = (
    ('Philip James', 'philip@inkpebble.com'),
)

MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'SMTP_Injection'
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'site@contactotter.com'
SERVER_EMAIL = 'site@contactotter.com'

SLACK_WEBHOOK_URL = get_env_variable('SLACK_WEBHOOK_URL')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_SESSION_REMEMBER=True
ACCOUNT_LOGOUT_REDIRECT_URL='/'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
        "ROUTING": "logtacts.routing.channel_routing",
    },
}

SWAGGER_SETTINGS = {
    'api_version': '0.1',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'delete',
    ],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'loggly': {
            '()': 'jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(message)s %(status_code)s %(module)s %(name)s %(pathname)s %(asctime)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'loggly-handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local5',
            'formatter': 'loggly',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'loggly',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'loggly-handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'post_to_social': {
            'handlers': ['console', 'loggly-handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'loggly_logs':{
            'handlers': ['console', 'loggly-handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
    },
}

GARGOYLE_SWITCH_DEFAULTS = {
    'read_only_mode': {
        'is_active': False,
        'label': 'Read-only mode',
        'description': 'Put the site into read-only mode, minus admin panel',
    }
}
