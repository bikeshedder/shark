from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SharkAuthConfig(AppConfig):
    name = "shark.auth"
    label = "shark_auth"
    verbose_name = _("Authentication and Authorization")
