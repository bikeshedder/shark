from xml.sax.saxutils import escape

from django.contrib import admin

from shark.sepa import models


class DirectDebitMandateAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address_html', 'iban', 'bic']
    list_filter = ['created', 'signed']
    search_fields = ['number', 'address', 'created']
    raw_id_fields = ['customer', 'document']

    def address_html(self, instance):
        return '<br/>'.join(map(escape, instance.address_lines))
    address_html.allow_tags = True
    address_html.short_description = models.DirectDebitMandate._meta.get_field('address').verbose_name
    address_html.admin_order_field = 'address'



class DirectDebitTransactionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'mandate', 'amount', 'invoice', 'batch', 'created']
    search_fields = ['customer__name']
    #raw_id_fields = ['customer', 'mandate', 'invoice', 'accounting_transaction', 'batch']
    raw_id_fields = ['customer', 'mandate', 'invoice', 'batch']


class DirectDebitBatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'executed']
    list_filter = ['created', 'executed']


admin.site.register(models.DirectDebitMandate, DirectDebitMandateAdmin)
admin.site.register(models.DirectDebitTransaction, DirectDebitTransactionAdmin)
admin.site.register(models.DirectDebitBatch, DirectDebitBatchAdmin)
