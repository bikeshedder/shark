# Django settings for shark project.

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'htdocs', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'htdocs', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Deprecated as of Django 1.4 but django-admin-tools still needs it.
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%h=(*j01ubrr#@(nq(h!j$dpcw_0^j4p-a9u&amp;c80f=x(2i7u@_'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    # default template context processors
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',

    # required by django-admin-tools
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'shark.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'shark.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

FORMAT_MODULE_PATH = 'shark.base.formats'

INSTALLED_APPS = (
    # Shark applications
    'shark',
    'shark.base',
    'shark.banking',
    'shark.billing',
    'shark.customer',
    'shark.documents',
    'shark.sepa',
    # Admin tools
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    # Django contrib
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    # Misc
    'autocomplete_light',
    'dinbrief',
    'taggit',
    'localflavor',
    'rest_framework',
)

ADMIN_TOOLS_INDEX_DASHBOARD = 'shark.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'shark.dashboard.CustomAppIndexDashboard'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    )
}

from decimal import Decimal
from datetime import timedelta

SHARK = {
    'VAT_RATE_CHOICES': (
        (Decimal('0.19'), u'19%'),
        (Decimal('0.07'), u'7%'),
        (Decimal('0.00'), string_concat(u'0%% (', _('tax free'), ')')),
    ),
    'INVOICE_PAYMENT_TIMEFRAME': timedelta(days=14),
    'INVOICE': {
        'BACKGROUND': {
            # 'FIRST_PAGE': ...
            # 'LATER_PAGE': ...
        },
        'SENDER': [
            "settings.SHARK['INVOICE']['SENDER']",
        ],
        'TERMS': [
            "settings.SHARK['INVOICE']['TERMS']",
        ],
        'NUMBER_GENERATOR': 'shark.utils.id_generators.YearCustomerN',
        'UNIT_CHOICES': [
            ('s', _('second [s]')),
            ('min', _('minute [min]')),
            ('h', _('hour [h]')),
            ('d', _('day [d]')),
            ('w', _('week [w]')),
            ('m', _('month [m]')),
            ('a', _('year [a]')),
        ],
    },
    'SEPA': {
        'CREDITOR_ID': '',
        'CREDITOR_NAME': '',
        'CREDITOR_COUNTRY': 'DE',
        'CREDITOR_IBAN': '',
        'CREDITOR_BIC': '',
        'DEFAULT_MANDATE_TYPE': 'CORE',
        'TRANSACTION_REFERENCE_PREFIX': '',
        'PRE_NOTIFICATION_EMAIL_FROM': '',
        'PRE_NOTIFICATION_EMAIL_BCC': [],
    },
    'MODELS': {
        'customer.Customer': 'customer.Customer',
        'billing.Invoice': 'billing.Invoice',
        'billing.InvoiceItem': 'billing.InvoiceItem',
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEST_RUNNER='django.test.runner.DiscoverRunner'
