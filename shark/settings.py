"""
Django settings for shark project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import LazyChoicesMixin

# Patch django_countries until new version is released
# This is the only dep that's blocking the upgrade
# https://github.com/SmileyChris/django-countries/issues/447#issuecomment-1890946593
LazyChoicesMixin.get_choices = lambda self: self._choices
LazyChoicesMixin.choices = property(
    LazyChoicesMixin.get_choices, LazyChoicesMixin.set_choices
)

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
    "shark.auth",
    "shark.base",
    "shark.billing",
    "shark.customer",
    "shark.project",
    "shark.tenant",
    "shark.sepa",
    "shark.id_generators",
    # Django Admin - order is mandatory
    # https://django-grappelli.readthedocs.io/en/latest/dashboard_setup.html#dashboard-setup
    "django.contrib.contenttypes",
    "grappelli.dashboard",
    "grappelli",
    "django.contrib.admin",
    # Django contrib
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Misc
    "dinbrief",
    "taggit",
    "localflavor",
    "rest_framework",
    "storages",
    "tailwind",
    "django_browser_reload",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "shark.auth.middleware.login_required",
    "shark.tenant.middleware.add_tenant",
    "shark.tenant.middleware.remove_tenant_capturing_group",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "shark.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shark.tenant.context_processors.tenant",
            ]
        },
    },
]

WSGI_APPLICATION = "shark.wsgi.application"
AUTH_USER_MODEL = "shark_auth.User"

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

LOGIN_URL = "/auth/login"
LOGIN_REDIRECT_URL = "/app/"
LOGOUT_REDIRECT_URL = LOGIN_URL

# Skip login_required middleware for these apps
LOGIN_REQUIRED_ROUTES = ["/app"]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "de"
LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]

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

TAILWIND_APP_NAME = "shark.base"
INTERNAL_IPS = [
    "127.0.0.1",
]

# Used for document storage
AWS_S3_ENDPOINT_URL = "http://minio:9000"
AWS_S3_ACCESS_KEY_ID = env.str("MINIO_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = env.str("MINIO_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "shark"
AWS_QUERYSTRING_AUTH = False

GRAPPELLI_INDEX_DASHBOARD = "shark.dashboard.CustomIndexDashboard"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
}

SHARK = {
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
