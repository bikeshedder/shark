from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "is_staff", "created_at"]
    search_fields = ["first_name", "last_name", "email"]

    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        (_("Personal info"), {"fields": ["first_name", "last_name"]}),
        (
            _("Permissions"),
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ],
            },
        ),
        (_("Important dates"), {"fields": ["last_login", "date_joined"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ("wide",),
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
