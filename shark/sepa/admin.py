from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django.utils.translation import override as trans_override

from shark.sepa.fields import get_creditor_fieldlist
from shark.utils.mail import send_templated_mail

from . import models


@admin.register(models.DirectDebitMandate)
class DirectDebitMandateAdmin(admin.ModelAdmin):
    list_display = ["customer", "address_html", "iban", "bic"]
    list_filter = ["created_at", "signed_at"]
    search_fields = ["number", "address", "created_at"]
    autocomplete_fields = ["customer"]

    @admin.display(description=_("address"))
    def address_html(self, instance: models.DirectDebitMandate):
        return format_html_join(
            "", "<p>{}</p>", ((line,) for line in instance.address_lines)
        )


@admin.register(models.DirectDebitTransaction)
class DirectDebitTransactionAdmin(admin.ModelAdmin):
    list_display = ["customer", "mandate", "amount", "invoice", "batch", "created_at"]
    search_fields = ["customer__name"]
    raw_id_fields = ["customer", "mandate", "invoice", "batch"]


@admin.register(models.DirectDebitBatch)
class DirectDebitBatchAdmin(admin.ModelAdmin):
    list_display = ["uuid", "created_at", "executed_at", "sepaxml_link"]
    list_filter = ["created_at", "executed_at"]
    actions = ["send_pre_notifications"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj is None:
            for field in get_creditor_fieldlist():
                form.base_fields[field].initial = getattr(request.tenant, field, "")

        return form

    @admin.display(description="SEPA XML")
    def sepaxml_link(self, instance: models.DirectDebitBatch):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("sepa_admin:directdebitbatch_sepaxml", args=(instance.pk,)),
            "Download",
        )

    @admin.display(description="Send pre-notifications for selected batches")
    def send_pre_notifications(self, request, queryset):
        for batch in queryset:
            transaction_list = list(
                batch.directdebittransaction_set.all().select_related("mandate")
            )
            for transaction in transaction_list:
                with trans_override(transaction.customer.language):
                    send_templated_mail(
                        subject_template="sepa/pre_notification_email_subject.txt",
                        body_template="sepa/pre_notification_email_body.txt",
                        dictionary={
                            "batch": batch,
                            "transaction": transaction,
                            "customer": transaction.customer,
                            "mandate": transaction.mandate,
                            "creditor_id": settings.SHARK["SEPA"]["CREDITOR_ID"],
                        },
                        from_email=settings.SHARK["SEPA"][
                            "PRE_NOTIFICATION_EMAIL_FROM"
                        ],
                        to=[
                            address.email
                            # TODO: no email_set exists
                            for address in transaction.customer.email_set.all()
                        ],
                        bcc=settings.SHARK["SEPA"]["PRE_NOTIFICATION_EMAIL_BCC"],
                    )
            self.message_user(
                request,
                ngettext(
                    "Send %(count)d pre-notification for batch %(batch_uuid)s",
                    "Send %(count)d pre-notifications for batch %(batch_uuid)s",
                    len(transaction_list),
                )
                % {
                    "count": len(transaction_list),
                    "batch_uuid": batch.uuid,
                },
            )
