"""
Django settings for shark project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy as _

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


ENV_FILE = ".env.ci" if env.bool("CI", False) else ".env"
environ.Env.read_env(os.path.join(BASE_DIR, ENV_FILE))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = [env("ALLOWED_HOSTS")]


# Application definition

INSTALLED_APPS = [
    # Shark applications
    "shark",
    "shark.base",
    "shark.billing",
    "shark.customer",
    "shark.project",
    "shark.sepa",
    # Admin tools
    "admin_tools",
    "admin_tools.theming",
    "admin_tools.menu",
    "admin_tools.dashboard",
    # Django contrib
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Misc
    "dinbrief",
    "taggit",
    "localflavor",
    "rest_framework",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "shark.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                "django.template.loaders.app_directories.Loader",
                "admin_tools.template_loaders.Loader",
            ],
        },
    },
]

WSGI_APPLICATION = "shark.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises
    # ImproperlyConfigured exception if not found
    "default": env.db(),
}

CACHES = {
    # Read os.environ['CACHE_URL'] and raises
    # ImproperlyConfigured exception if not found.
    "default": env.cache(),
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "htdocs" / "static"

# Media files

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "htdocs" / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


FORMAT_MODULE_PATH = "shark.base.formats"


# Used for document storage
AWS_S3_ENDPOINT_URL = "http://minio:9000"
AWS_S3_ACCESS_KEY_ID = env.str("MINIO_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = env.str("MINIO_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "shark"
AWS_QUERYSTRING_AUTH = False

ADMIN_TOOLS_INDEX_DASHBOARD = "shark.dashboard.CustomIndexDashboard"
ADMIN_TOOLS_APP_INDEX_DASHBOARD = "shark.dashboard.CustomAppIndexDashboard"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
}

SHARK = {
    "VAT_RATE_CHOICES": (
        (Decimal("0.19"), "19%"),
        (Decimal("0.07"), "7%"),
        (Decimal("0.00"), "0%"),
    ),
    "CUSTOMER": {
        "NUMBER_GENERATOR": "shark.utils.id_generators.InitialAsNumber",
        "TYPE_CHOICES": [("default", _("Default"))],
        "TYPE_DEFAULT": "default",
    },
    "INVOICE": {
        "BACKGROUND": {
            # 'FIRST_PAGE': ...
            # 'LATER_PAGE': ...
        },
        "SENDER": {
            "name": "settings.SHARK['INVOICE']['SENDER']['name']",
            "street": "settings.SHARK['INVOICE']['SENDER']['street']",
            "postal_code": "settings.SHARK['INVOICE']['SENDER']['postal_code']",
            "city": "settings.SHARK['INVOICE']['SENDER']['city']",
        },
        "TERMS": [
            "settings.SHARK['INVOICE']['TERMS']",
        ],
        "NUMBER_GENERATOR": "shark.utils.id_generators.YearCustomerN",
        "UNIT_CHOICES": [
            ("s", _("second [s]")),
            ("min", _("minute [min]")),
            ("h", _("hour [h]")),
            ("d", _("day [d]")),
            ("w", _("week [w]")),
            ("m", _("month [m]")),
            ("a", _("year [a]")),
        ],
        "PAYMENT_TIMEFRAME": timedelta(days=14),
    },
    "SEPA": {
        "CREDITOR_ID": "",
        "CREDITOR_NAME": "",
        "CREDITOR_COUNTRY": "DE",
        "CREDITOR_IBAN": "",
        "CREDITOR_BIC": "",
        "DEFAULT_MANDATE_TYPE": "CORE",
        "TRANSACTION_REFERENCE_PREFIX": "",
        "PRE_NOTIFICATION_EMAIL_FROM": "",
        "PRE_NOTIFICATION_EMAIL_BCC": [],
    },
}
