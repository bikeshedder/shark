from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shark.utils.fields import get_address_fieldlist

from . import models


@admin.register(models.Tenant)
class TenantAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ["name"]}),
        (
            _("address"),
            {"fields": get_address_fieldlist("address")},
        ),
    )


def TenantAwareAdmin(cls):
    """
    Decorator to be used for ModelAdmins

    This sets an object's Tenant FK to the Tenant that is returned from the middleware
    """
    save_model = getattr(cls, "save_model")

    def save_model_with_tenant(self, request, obj, form, change):
        # Only apply at object creation
        if obj.pk is None:
            tenant = request.tenant
            if tenant is None:
                raise Exception("Cannot save without tenant. Create a Tenant first.")
            setattr(obj, "tenant", request.tenant)

        save_model(self, request, obj, form, change)

    setattr(cls, "save_model", save_model_with_tenant)
    return cls
