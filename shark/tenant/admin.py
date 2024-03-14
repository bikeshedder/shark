from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shark.sepa.fields import get_creditor_fieldlist
from shark.utils.fields import get_address_fieldlist

from . import models


class TenantMemberAdmin(admin.StackedInline):
    model = models.TenantMember
    extra = 0
    inline_classes = ["grp-collapse grp-open"]


@admin.register(models.Tenant)
class TenantAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "name",
                    "customer_number_generator",
                    "invoice_number_generator",
                ]
            },
        ),
        (
            _("address"),
            {"fields": get_address_fieldlist()},
        ),
        (
            _("creditor"),
            {"fields": get_creditor_fieldlist()},
        ),
    )

    inlines = [TenantMemberAdmin]


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
