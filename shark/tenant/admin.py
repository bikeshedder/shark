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


# Decorator to be used for any objects that are directly tied to a Tenant
#
# Tenants should disappear completely from the UI and only act as way to
# isolate DB entries from other Tenants
def TenantAwareAdmin(cls):
    save_model = getattr(cls, "save_model")

    def save_model_with_tenant(self, request, obj, form, change):
        if obj.pk is None:
            tenant = request.tenant
            if tenant is None:
                raise Exception("Cannot save without tenant. Create a Tenant first.")
            setattr(obj, "tenant", request.tenant)

        save_model(self, request, obj, form, change)

    setattr(cls, "save_model", save_model_with_tenant)
    return cls
