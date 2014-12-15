# -*- coding: UTF-8 -*-

from datetime import date
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.formats import date_format
from django.utils.html import escape
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from shark import get_model, get_admin_change_url
from shark import get_admin_changelist_url
from shark.billing import models

Customer = get_model('customer.Customer')
Invoice = get_model('billing.Invoice')


class InvoiceItemInline(admin.TabularInline):
    model = models.InvoiceItem
    extra = 3
    ordering = ('position',)
    exclude = ('customer',)


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('general'), {'fields': ('customer', 'number', 'language') }),
        (_('address'), {'fields': ('sender', 'recipient') }),
        (_('dates'), {'fields': ('created', 'reminded', 'paid') }),
    )
    inlines = [InvoiceItemInline]
    raw_id_fields = ('customer',)
    list_display = ('number', 'get_customer', 'get_recipient', 'net',
            'gross', 'created', 'paid', 'is_okay', 'invoice_pdf', 'correction_pdf')
    list_editable = ('paid',)
    list_display_links = ('number',)
    list_select_related = True
    ordering = ('-created',)
    search_fields = ('number', 'customer__number', 'customer__name', 'recipient')
    list_filter = ('created', 'paid',)
    date_hierarchy = 'created'
    actions = ('total_value_action',)
    save_on_top = True

    def get_customer(self, obj):
        return u'<a href="%s">%s</a>' % (
                get_admin_change_url(obj.customer), obj.customer)
    get_customer.short_description = _('Customer')
    get_customer.admin_order_field = 'customer'
    get_customer.allow_tags = True

    def get_recipient(self, obj):
        return u'<br/>'.join(map(escape, obj.recipient_lines))
    get_recipient.short_description = _('Recipient')
    get_recipient.allow_tags = True

    def invoice_pdf(self, obj):
        view = u'<a href="%s">View</a>' % (
            reverse('billing_admin:invoice_pdf', args=(obj.number,)))
        download = u'<a href="%s?download">Download</a>' % (
            reverse('billing_admin:invoice_pdf', args=(obj.number,)))
        return '%s | %s' % (view, download)
    invoice_pdf.short_description = 'Invoice'
    invoice_pdf.allow_tags = True

    def correction_pdf(self, obj):
        view = u'<a href="%s">View</a>' % (
            reverse('billing_admin:correction_pdf', args=(obj.number,)))
        download = u'<a href="%s?download">Download</a>' % (
            reverse('billing_admin:correction_pdf', args=(obj.number,)))
        return '%s | %s' % (view, download)
    correction_pdf.short_description = 'Correction'
    correction_pdf.allow_tags = True

    def response_add(self, request, obj, *args, **kwargs):
        obj.recalculate()
        obj.save()
        return super(InvoiceAdmin, self).response_add(request, obj, *args, **kwargs)

    def response_change(self, request, obj, *args, **kwargs):
        obj.recalculate()
        obj.save()
        return super(InvoiceAdmin, self).response_change(request, obj, *args, **kwargs)

    def total_value_action(self, request, queryset):
        net = Decimal(0)
        gross = Decimal(0)
        for invoice in queryset:
            net += invoice.net
            gross += invoice.gross
        value = ugettext('%(net)s net, %(gross)s gross') % {
                'net': net, 'gross': gross }
        self.message_user(request, ungettext(
            'Total value of %(count)d invoice: %(value)s',
            'Total value of %(count)d invoices: %(value)s',
            len(queryset)) % { 'count': len(queryset), 'value': value })
    total_value_action.short_description = _('Calculate total value of selected invoices')



class InvoiceItemAdmin(admin.ModelAdmin):
    raw_id_fields = ('customer', 'invoice')
    list_display = ('customer', 'invoice', 'position', 'sku', 'text',
            'begin', 'end', 'quantity', 'price', 'total', 'discount',
            'vat_rate')
    list_display_links = ('position', 'text')
    list_filter = ('begin', 'end', 'vat_rate')
    ordering = ('customer__number', 'invoice__number', 'position')
    search_fields = ('invoice__number', 'customer__number', 'sku', 'text')
    actions = ('action_create_invoice',)

    def action_create_invoice(self, request, queryset):
        # customer_id -> items
        items_dict = {}
        # [(customer, items)]
        customer_items_list = []
        for item in queryset \
                .filter(invoice=None) \
                .order_by('text'):
            try:
                items = items_dict[item.customer_id]
            except KeyError:
                items = items_dict[item.customer_id] = []
                customer_items_list.append((item.customer, items))
            items.append(item)
        # create invoices
        for customer, items in customer_items_list:
            invoice = Invoice()
            invoice.customer = customer
            invoice.save()
            for position, item in enumerate(items, 1):
                item.position = position
                item.invoice = invoice
                item.save()
            invoice.recalculate()
            invoice.save()
        return HttpResponseRedirect(get_admin_changelist_url(Invoice))
    action_create_invoice.short_description = _('Create invoice(s) for selected item(s)')


admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.InvoiceItem, InvoiceItemAdmin)
