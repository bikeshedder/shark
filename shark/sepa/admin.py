from xml.sax.saxutils import escape

import autocomplete_light
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from shark.sepa import models


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

    def sepaxml_link(self, instance):
        return u'<a href="%s">%s</a>' % (
            reverse('sepa_admin:directdebitbatch_sepaxml', args=(instance.pk,)),
            'Download',
        )
    sepaxml_link.allow_tags = True
    sepaxml_link.short_description = u'SEPA XML'


admin.site.register(models.DirectDebitMandate, DirectDebitMandateAdmin)
admin.site.register(models.DirectDebitTransaction, DirectDebitTransactionAdmin)
admin.site.register(models.DirectDebitBatch, DirectDebitBatchAdmin)
