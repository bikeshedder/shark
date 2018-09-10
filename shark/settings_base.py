"""
Django settings for shark project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l_8$c18y1=urm5+(0)6lijec%&a9+%n+i4ufe6y)h&j&)bj$6e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    # Shark applications
    'shark',
    'shark.base',
    'shark.banking',
    'shark.billing',
    'shark.customer',
    'shark.documents',
    'shark.issue',
    'shark.project',
    'shark.sepa',
    # Admin tools
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    # Django contrib
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Misc
    'dinbrief',
    'taggit',
    'localflavor',
    'rest_framework',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shark.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.app_directories.Loader',
                'admin_tools.template_loaders.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'shark.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
'''
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
'''


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'htdocs', 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'htdocs', 'media')

FORMAT_MODULE_PATH = 'shark.base.formats'

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
        (Decimal('0.19'), '19%'),
        (Decimal('0.07'), '7%'),
        (Decimal('0.00'), format_lazy('0% ({})', _('tax free'))),
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
