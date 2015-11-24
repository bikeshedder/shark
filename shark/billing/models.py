# -*- coding: UTF-8 -*-

from decimal import Decimal
from datetime import datetime, date, timedelta
import inspect

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _

from shark import get_model_name
from shark.customer.fields import AddressField
from shark.utils.id_generators import IdField
from shark.utils.fields import LanguageField
from shark.utils.rounding import round_to_centi
from shark.utils.importlib import import_object

INVOICE_PAYMENT_TIMEFRAME = settings.SHARK.get('INVOICE_PAYMENT_TIMEFRAME', 14)
VAT_RATE_CHOICES = settings.SHARK.get('VAT_RATE_CHOICES', (Decimal(0), '0%'))
CUSTOMER_MODEL = get_model_name('customer.Customer')
INVOICE_SENDER = settings.SHARK['INVOICE']['SENDER']
UNIT_CHOICES = settings.SHARK['INVOICE']['UNIT_CHOICES']
NUMBER_GENERATOR = settings.SHARK['INVOICE']['NUMBER_GENERATOR']

if isinstance(NUMBER_GENERATOR, basestring):
    NUMBER_GENERATOR = import_object(NUMBER_GENERATOR)
if inspect.isclass(NUMBER_GENERATOR):
    NUMBER_GENERATOR = NUMBER_GENERATOR()


class Invoice(models.Model):
    #
    # general
    #
    customer = models.ForeignKey(CUSTOMER_MODEL,
            verbose_name=_('Customer'))
    TYPE_INVOICE = 'invoice'
    TYPE_CORRECTION = 'correction'
    TYPE_CHOICES = (
        (TYPE_INVOICE, _('Invoice')),
        (TYPE_CORRECTION, _('Correction of invoice')),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INVOICE)
    number = IdField(generator=NUMBER_GENERATOR)
    language = LanguageField(blank=True,
            help_text=_('This field will be automatically filled with the language of the customer. If no language for the customer is specified the default language (%s) will be used.' % settings.LANGUAGE_CODE))

    PAYMENT_TYPE_INVOICE = 'invoice'
    PAYMENT_TYPE_DIRECT_DEBIT = 'direct_debit'
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_INVOICE, _('Invoice')),
        (PAYMENT_TYPE_DIRECT_DEBIT, _('Direct debit')),
    )
    payment_type = models.CharField(_('Payment Type'),
            max_length=20,
            choices=PAYMENT_TYPE_CHOICES,
            default='invoice',
            help_text=_('Will be copied from customer\'s preferences automatically.'))

    #
    # address
    #
    sender = AddressField(blank=True,
            default='\n'.join(INVOICE_SENDER))
    recipient = AddressField(blank=True,
            help_text=_('This field will be automatically filled with the address of the customer.'))

    net = models.DecimalField(max_digits=10, decimal_places=2,
            default=Decimal('0.00'),
            verbose_name=_('net'))
    gross = models.DecimalField(max_digits=10, decimal_places=2,
            default=Decimal('0.00'),
            verbose_name=_('gross'))

    #
    # status
    #
    created = models.DateField(
            default=date.today,
            verbose_name=_('Created'))
    reminded = models.DateField(blank=True, null=True,
            verbose_name=_('Reminded'))
    paid = models.DateField(blank=True, null=True,
            verbose_name=_('Paid'))

    class Meta:
        db_table = 'billing_invoice'
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        unique_together = (('customer', 'number'),)
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s %s' % (_('Invoice'), self.number)

    def save(self, *args, **kwargs):
        if not self.recipient:
            self.recipient = self.customer.address
        if not self.language:
            self.language = self.customer.language \
                    if self.customer.language \
                    else settings.LANGUAGE_CODE
        super(Invoice, self).save(*args, **kwargs)

    def is_okay(self):
        if self.paid:
            return True
        if self.reminded is None:
            deadline = self.created + INVOICE_PAYMENT_TIMEFRAME
        else:
            deadline = self.reminded + INVOICE_PAYMENT_TIMEFRAME
        return date.today() <= deadline
    is_okay.short_description = _('Okay')
    is_okay.boolean = True

    @property
    def items(self):
        if not hasattr(self, '_item_cache'):
            self._item_cache = self.item_set.all()
        return self._item_cache

    @property
    def correction(self):
        c = Invoice(
                customer=self.customer,
                number=self.number,
                language=self.language,
                sender=self.sender,
                recipient=self.recipient)
        c._item_cache = [item.clone() for item in self.items]
        for item in c.items:
            item.quantity = -item.quantity
        c.recalculate()
        return c

    #
    # status
    #
    created = models.DateField(
            default=date.today,
            verbose_name=_('Created'))
    reminded = models.DateField(blank=True, null=True,
            verbose_name=_('Reminded'))
    paid = models.DateField(blank=True, null=True,
            verbose_name=_('Paid'))

    def recalculate(self):
        self.net = sum(item.total for item in self.items)
        vat_amount = sum(vat_amount for vat_rate, vat_amount in self.vat)
        self.gross = self.net + vat_amount

    @property
    def vat(self):
        '''
        Return a list of (vat_rate, amount) tuples.
        '''
        # create a dict which maps the vat rate to a list of items
        vat_dict = {}
        for item in self.items:
            if item.vat_rate == 0:
                continue
            vat_dict.setdefault(item.vat_rate, []).append(item)
        # sum up item per vat rate and create an ordered list of
        # (vat_rate, vat_amount) tuples.
        vat_list = []
        for vat_rate, items in vat_dict.iteritems():
            amount = sum(item.total for item in items)
            vat_amount = round_to_centi(vat_rate * amount)
            vat_list.append((vat_rate, vat_amount))
        vat_list.sort()
        return vat_list

    @property
    def vat_items(self):
        # XXX either this or the vat property should be dropped
        class VatItem(object):
            def __init__(self, rate, amount):
                self.rate = rate
                self.amount = amount
        return [VatItem(*t) for t in self.vat]


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='item_set',
            blank=True, null=True,
            verbose_name=_('invoice'))
    customer = models.ForeignKey(CUSTOMER_MODEL,
            verbose_name=_('customer'))
    position = models.PositiveIntegerField(blank=True, null=True,
            verbose_name=_('position'))
    quantity = models.DecimalField(max_digits=10, decimal_places=2,
            default=Decimal('1'),
            verbose_name=_('quantity'))
    sku = models.CharField(max_length=20, blank=True,
            verbose_name=_('SKU'),
            help_text=_('Stock-keeping unit (e.g. Article number)'))
    text = models.CharField(max_length=200,
            verbose_name=_('description'))
    begin = models.DateField(blank=True, null=True,
            verbose_name=_('begin'))
    end = models.DateField(blank=True, null=True,
            verbose_name=_('end'))
    price = models.DecimalField(max_digits=10, decimal_places=2,
            verbose_name=_('price'))
    unit = models.CharField(max_length=10, blank=True,
            choices=UNIT_CHOICES,
            verbose_name=_('unit'))
    discount = models.DecimalField(max_digits=3, decimal_places=2,
            default=Decimal('0.00'),
            verbose_name=('discount'))
    vat_rate = models.DecimalField(max_digits=3, decimal_places=2,
            choices=VAT_RATE_CHOICES,
            verbose_name=('VAT rate'))

    class Meta:
        db_table = 'billing_invoice_item'
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        unique_together = (('invoice', 'position'),)
        ordering = ('position',)

    def __unicode__(self):
        return u'#%d %s' % (self.position or 0, self.text)

    def clone(self):
        return InvoiceItem(
                invoice=self.invoice,
                customer=self.customer,
                position=self.position,
                quantity=self.quantity,
                sku=self.sku,
                text=self.text,
                begin=self.begin,
                end=self.end,
                price=self.price,
                unit=self.unit,
                discount=self.discount,
                vat_rate=self.vat_rate)

    def save(self):
        if not self.customer_id:
            if self.invoice_id:
                self.customer_id = self.invoice.customer_id
            else:
                raise RuntimeError('The customer must be set if no invoice is given')
        super(InvoiceItem, self).save()

    def get_period(self):
        if self.begin and self.end:
            begin = date_format(self.begin, 'SHORT_DATE_FORMAT')
            end = date_format(self.end, 'SHORT_DATE_FORMAT') \
                    if self.end is not None \
                    else _('one-time')
            return u'%s – %s' % (begin, end)
        else:
            return None
    get_period.short_description = _('Billing period')
    period = property(get_period)

    @property
    def date(self):
        return self.begin or self.end \
                if bool(self.begin) != bool(self.end) \
                else None

    def get_subtotal(self):
        return round_to_centi(self.quantity * self.price)
    get_subtotal.short_description = _('Subtotal')
    subtotal = property(get_subtotal)

    @property
    def discount_percentage(self):
        return self.discount * 100

    @property
    def discount_amount(self):
        return round_to_centi(self.discount * self.subtotal)

    def get_total(self):
        return self.subtotal - self.discount_amount
    get_total.short_description = _('Sum of line')
    total = property(get_total)
