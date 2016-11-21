from xml.sax.saxutils import escape

from autocomplete_light import shortcuts as autocomplete_light
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.utils.translation import override as trans_override

from shark.sepa import models
from shark.utils.mail import send_templated_mail


class DirectDebitMandateAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address_html', 'iban', 'bic']
    list_filter = ['created', 'signed']
    search_fields = ['number', 'address', 'created']
    form = autocomplete_light.modelform_factory(models.DirectDebitMandate, exclude=[])
    raw_id_fields = ['document']

    def address_html(self, instance):
        return u'<br/>'.join(map(escape, instance.address_lines))
    address_html.allow_tags = True
    address_html.short_description = _('address')


class DirectDebitTransactionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'mandate', 'amount', 'invoice', 'batch', 'created']
    search_fields = ['customer__name']
    #raw_id_fields = ['customer', 'mandate', 'invoice', 'accounting_transaction', 'batch']
    raw_id_fields = ['customer', 'mandate', 'invoice', 'batch']


class DirectDebitBatchAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'created', 'executed', 'sepaxml_link']
    list_filter = ['created', 'executed']
    actions = ['send_pre_notifications']

    def sepaxml_link(self, instance):
        return u'<a href="%s">%s</a>' % (
            reverse('sepa_admin:directdebitbatch_sepaxml', args=(instance.pk,)),
            'Download',
        )
    sepaxml_link.allow_tags = True
    sepaxml_link.short_description = u'SEPA XML'

    def send_pre_notifications(self, request, queryset):
        for batch in queryset:
            transaction_list = list(batch.directdebittransaction_set.all() \
                    .select_related('mandate'))
            for transaction in transaction_list:
                with trans_override(transaction.customer.language):
                    send_templated_mail(
                        subject_template='sepa/pre_notification_email_subject.txt',
                        body_template='sepa/pre_notification_email_body.txt',
                        dictionary={
                            'batch': batch,
                            'transaction': transaction,
                            'customer': transaction.customer,
                            'mandate': transaction.mandate,
                            'creditor_id': settings.SHARK['SEPA']['CREDITOR_ID'],
                        },
                        from_email=settings.SHARK['SEPA']['PRE_NOTIFICATION_EMAIL_FROM'],
                        to=[address.email for address in transaction.customer.email_set.all()],
                        bcc=settings.SHARK['SEPA']['PRE_NOTIFICATION_EMAIL_BCC'],
                    )
            self.message_user(request, ungettext(
                'Send %(count)d pre-notification for batch %(batch_uuid)s',
                'Send %(count)d pre-notifications for batch %(batch_uuid)s',
                len(transaction_list)
            ) % {
                'count': len(transaction_list),
                'batch_uuid': batch.uuid,
            })
    send_pre_notifications.short_description = _('Send pre-notifications for selected batches')


admin.site.register(models.DirectDebitMandate, DirectDebitMandateAdmin)
admin.site.register(models.DirectDebitTransaction, DirectDebitTransactionAdmin)
admin.site.register(models.DirectDebitBatch, DirectDebitBatchAdmin)
