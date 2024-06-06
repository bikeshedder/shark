from .settings import *  # noqa

DEBUG = True

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    },
}


# Tailwind Server Config
TAILWIND_APP_NAME = "shark.base"
INTERNAL_IPS = [
    "127.0.0.1",
]
