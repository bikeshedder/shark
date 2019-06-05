# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from taggit.managers import TaggableManager

from shark.utils.fields import OldAddressField, AddressField, LanguageField
from shark.utils.id_generators import IdField
from shark.utils.settings import get_settings_instance, get_settings_value

NUMBER_GENERATOR = get_settings_instance('CUSTOMER.NUMBER_GENERATOR')
CUSTOMER_TYPE_CHOICES = get_settings_value('CUSTOMER.TYPE_CHOICES')
CUSTOMER_TYPE_DEFAULT = get_settings_value('CUSTOMER.TYPE_DEFAULT')


class CustomerTypeField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        kwargs.setdefault('choices', CUSTOMER_TYPE_CHOICES)
        kwargs.setdefault('default', CUSTOMER_TYPE_DEFAULT)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        del kwargs["default"]
        return name, path, args, kwargs


class Customer(models.Model):
    number = IdField(generator=NUMBER_GENERATOR)
    # XXX add_unique constraint
    name = models.CharField(max_length=50, blank=True)
    # FIXME add choices
    type = CustomerTypeField(db_index=True)
    primary_admin = models.ForeignKey(settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            blank=True, null=True)

    address = OldAddressField(_('address'), blank=True) # XXX deprecated

    # Language to be used when communicating with the customer. This
    # field is mainly used to determine which language to use when
    # generating invoices and email messages.
    language = LanguageField(_('language'), blank=True)

    # rates when creating invoices
    hourly_rate = models.DecimalField(_('hourly rate'),
            max_digits=7, decimal_places=2, blank=True, null=True)
    daily_rate = models.DecimalField(_('daily rate'),
            max_digits=7, decimal_places=2, blank=True, null=True)

    tags = TaggableManager(blank=True)

    INVOICE_DISPATCH_TYPE_EMAIL = 'email'
    INVOICE_DISPATCH_TYPE_FAX = 'fax'
    INVOICE_DISPATCH_TYPE_MAIL = 'mail'
    # XXX move this to the billing app?
    INVOICE_DISPATCH_TYPE_CHOICES = (
        (INVOICE_DISPATCH_TYPE_EMAIL, _('via email')),
        (INVOICE_DISPATCH_TYPE_FAX, _('via FAX')),
        (INVOICE_DISPATCH_TYPE_MAIL, _('via mail')),
    )
    invoice_dispatch_type = models.CharField(max_length=20,
            choices=INVOICE_DISPATCH_TYPE_CHOICES,
            default='email',
            verbose_name=_('Invoice dispatch type'))
    PAYMENT_TYPE_INVOICE = 'invoice'
    PAYMENT_TYPE_DIRECT_DEBIT = 'direct_debit'
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_INVOICE, _('Invoice')),
        (PAYMENT_TYPE_DIRECT_DEBIT, _('Direct debit')),
    )
    payment_type = models.CharField(max_length=20,
            choices=PAYMENT_TYPE_CHOICES,
            default='invoice',
            verbose_name=_('Payment Type'))
    vatin = models.CharField(max_length=14, blank=True,
            verbose_name=_('VATIN'),
            help_text=_('Value added tax identification number'))

    enabled = models.BooleanField(default=True)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        return self.number

    @property
    def active(self):
        # The customer active flag does not depend on anything but
        # the enabled flag.
        return self.enabled

    @property
    def vat_required(self):
        # VAT for invoices is required if customer...
        # ...lives in Germany
        # ...lives in the EU and does not have a VATIN
        return self.country.id == 'DE' or \
                (self.country.eu and not self.vatin)


class CustomerComment(models.Model):
    customer = models.ForeignKey('customer.Customer',
            on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
            blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class CustomerContact(models.Model):
    customer = models.ForeignKey('customer.Customer',
            on_delete=models.CASCADE)

    # TODO add type (person, general,... ?)
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = (
            (GENDER_MALE, _('Male')),
            (GENDER_FEMALE, _('Female')),
    )
    gender = models.CharField(max_length=1, blank=True,
            choices=GENDER_CHOICES,
            verbose_name=_('Gender'))
    TITLE_CHOICES = (
            ('Herr', 'Herr'),
            ('Frau', 'Frau'),
            ('Fräulein', 'Fräulein'),
            ('Dr.', 'Dr.'),
            ('Dr. Dr.', 'Dr. Dr.'),
            ('Prof. Dr.', 'Prof. Dr.'),
    )
    title = models.CharField(max_length=20, blank=True,
            choices = TITLE_CHOICES,
            verbose_name=_('Salutation'),
            help_text='z.B. Herr, Frau, Dr., Prof.,...')
    first_name = models.CharField(max_length=20, blank=True,
            verbose_name=_('First name'))
    last_name = models.CharField(max_length=20, blank=True,
            verbose_name=_('Last name'))

    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    mobile_number = models.CharField(max_length=50, blank=True)
    fax_number = models.CharField(max_length=50, blank=True)


class CustomerAddress(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    address = AddressField(prefix='')
    sender_line = models.CharField(max_length=100, blank=True, default='')
    invoice_address = models.BooleanField(default=False)
