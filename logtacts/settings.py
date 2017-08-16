"""
Django settings for logtacts project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import os
import raven
import warnings

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from unipath import Path


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))


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

ALLOWED_HOSTS = ['*']

SITE_ID=1

PROJECT_ROOT = Path(BASE_DIR)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = PROJECT_ROOT.child('media')
STATIC_ROOT = PROJECT_ROOT.child('dist')
STATICFILES_DIRS = (
    PROJECT_ROOT.child('static'),
    PROJECT_ROOT.child('node_modules').child('bootstrap').child('dist'),
    PROJECT_ROOT.child('node_modules').child('jquery').child('dist'),
)
STATIC_URL = '/static/'

ENVIRONMENT = 'dev'

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
                'logtacts.context_processors.selected_settings',
                'contacts.processors.book',
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
    'django.contrib.flatpages',
    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.foursquare',
    'allauth.socialaccount.providers.google',
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
    'captcha',
    'raven.contrib.django.raven_compat',
    # ContactOtter Apps
    'contacts.apps.ContactConfig',
    'invitations.apps.InvitationConfig',
    'profiles.apps.ProfilesConfig',
    'chats.apps.ChatsConfig',
    'payments.apps.PaymentsConfig',
)

MIDDLEWARE_CLASSES = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
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
    'contacts.middleware.ContactBookMiddleware',
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

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

ADMINS = (
    ('Philip James', 'philip@inkpebble.com'),
)

MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_variable('EMAIL_USERNAME')
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
ACCOUNT_SIGNUP_FORM_CLASS='profiles.forms.ReCaptchaSignupForm'
ACCOUNT_UNIQUE_EMAIL=True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email', 'https://www.googleapis.com/auth/contacts.readonly'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

RECAPTCHA_PRIVATE_KEY = get_env_variable('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PUBLIC_KEY = get_env_variable('RECAPTCHA_PUBLIC_KEY')
NOCAPTCHA = True

STRIPE_PUBLIC_KEY = get_env_variable('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = get_env_variable('STRIPE_SECRET_KEY')

NEXMO_KEY = get_env_variable('NEXMO_KEY')
NEXMO_SECRET = get_env_variable('NEXMO_SECRET')
NEXMO_NUMBER = get_env_variable('NEXMO_NUMBER')

AWS_ACCESS_KEY = get_env_variable('AWS_ACCESS_KEY')
AWS_SECRET_KEY = get_env_variable('AWS_SECRET_KEY')

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
        "ROUTING": "logtacts.routing.channel_routing",
    },
}

RAVEN_CONFIG = {
    'dsn': get_env_variable('SENTRY_URL'),
}

try:
    RAVEN_CONFIG['release'] = raven.fetch_git_sha(os.path.dirname(os.path.dirname(__file__)))
except:
    pass

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
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
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
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
            'formatter': 'verbose',
        },
        'console_json': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'loggly',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
        'django.request': {
            'handlers': ['console', 'loggly-handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'scripts': {
            'handlers': ['console', 'loggly-handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'loggly_logs':{
            'handlers': ['console_json', 'loggly-handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

GARGOYLE_SWITCH_DEFAULTS = {
    'read_only_mode': {
        'is_active': False,
        'label': 'Read-only mode',
        'description': 'Put the site into read-only mode, minus admin panel',
    },
    'multi_book': {
        'is_active': False,
        'label': 'Allow one user to be part of multiple books',
        'description': 'Users can have and manage multiple books',
    },
    'enable_payments': {
        'is_active': False,
        'label': 'Enable payments',
        'description': 'Turn on Stripe payments',
    },
    'import_from_google': {
        'is_active': False,
        'label': "Import from Google",
        'description': 'Enable importing contacts from Google',
    },
    'scheduled_reminders': {
        'is_active': False,
        'label': 'Scheduled reminders on contacts',
        'description': 'Allow setting reminder frequency on individual contacts',
    },
}
