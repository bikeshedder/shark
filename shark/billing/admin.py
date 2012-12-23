# -*- coding: UTF-8 -*-

from datetime import date
from datetime import datetime

from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils.formats import date_format
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.db.models import get_model

from shark.billing import models


CUSTOMER_MODEL = settings.SHARK.get('CUSTOMER_MODEL', 'customer.Customer')
Customer = get_model(*CUSTOMER_MODEL.split('.'))
INVOICE_MODEL = settings.SHARK.get('INVOICE_MODEL', 'billing.Invoice')
Invoice = get_model(*INVOICE_MODEL.split('.'))


class InvoiceItemInline(admin.TabularInline):
    model = models.InvoiceItem
    extra = 3
    ordering = ('position',)


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Allgemeines', {'fields': ('customer', 'number') }),
        ('Adresse', {'fields': ('address',) }),
        ('Daten', {'fields': ('created', 'reminded', 'paid') }),
    )
    inlines = [InvoiceItemInline]
    raw_id_fields = ('customer',)
    list_display = ('number', 'get_customer', 'get_address', 'net',
            'gross', 'created', 'paid', 'is_okay', 'invoice_pdf')
    list_editable = ('paid',)
    list_display_links = ('number',)
    list_select_related = True
    ordering = ('-created',)
    search_fields = ('number', 'customer__number', 'customer__name', 'address')
    list_filter = ('created', 'paid',)
    date_hierarchy = 'created'
    actions = ('create_document_action', 'remind_action')
    save_on_top = True

    def get_customer(self, obj):
        return u'<a href="%s">%s</a>' % (
            reverse('admin:customer_customer_change', args=(obj.customer.id,)), obj.customer.name)
    get_customer.short_description = _('Customer')
    get_customer.admin_order_field = 'customer'
    get_customer.allow_tags = True

    def get_address(self, obj):
        return u'<br/>'.join(map(escape, obj.address_lines))
    get_address.short_description = _('Address')
    get_address.allow_tags = True

    def invoice_pdf(self, obj):
        view = u'<a href="%s">View</a>' % (
            reverse('billing_admin:invoice_pdf', args=(obj.pk,)))
        download = u'<a href="%s?download">Download</a>' % (
            reverse('billing_admin:invoice_pdf', args=(obj.pk,)))
        return '%s | %s' % (view, download)
    invoice_pdf.short_description = 'Invoice'
    invoice_pdf.allow_tags = True


class InvoiceItemAdmin(admin.ModelAdmin):
    raw_id_fields = ('customer', 'invoice')
    list_display = ('customer', 'invoice', 'position', 'sku', 'text', 'begin', 'end', 'price', 'total', 'discount', 'vat_rate')
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
        for item in queryset:
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
            invoice.address = customer.address
            invoice.save()
            for position, item in enumerate(items, 1):
                item.position = position
                item.invoice = invoice
                item.save()
            invoice.recalculate()
            invoice.save()
    action_create_invoice.short_description = _('Create invoice(s) for selected item(s)')


admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.InvoiceItem, InvoiceItemAdmin)
