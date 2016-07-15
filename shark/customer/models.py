# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from shark.customer.fields import AddressField
from shark.utils.fields import LanguageField
from shark.utils.id_generators import IdField, DaysSinceEpoch
from shark import get_model_name, is_model_overridden
from taggit.managers import TaggableManager


class BaseCustomer(models.Model):
    # FIXME look up customer number generator from settings
    number = IdField(generator=DaysSinceEpoch())
    address = AddressField(_('address')) # XXX deprecated

    # Language to be used when communicating with the customer. This
    # field is mainly used to determine which language to use when
    # generating invoices and email messages.
    language = LanguageField(_('language'), blank=True)

    # rates when creating invoices
    hourly_rate = models.DecimalField(_('hourly rate'),
            max_digits=7, decimal_places=2, blank=True, null=True)
    daily_rate = models.DecimalField(_('daily rate'),
            max_digits=7, decimal_places=2, blank=True, null=True)

    tags = TaggableManager()

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
        abstract = True
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __unicode__(self):
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


class Customer(BaseCustomer):

    class Meta(BaseCustomer.Meta):
        abstract = is_model_overridden('customer.Customer')


class CustomerComment(models.Model):
    customer = models.ForeignKey(get_model_name('customer.Customer'))
    #user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class CustomerContact(models.Model):
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
            help_text=u'z.B. Herr, Frau, Dr., Prof.,...')
    first_name = models.CharField(max_length=20, blank=True,
            verbose_name=_('First name'))
    last_name = models.CharField(max_length=20, blank=True,
            verbose_name=_('Last name'))

    phone_number = models.CharField(max_length=50, blank=True)
    mobile_number = models.CharField(max_length=50, blank=True)
    fax_number = models.CharField(max_length=50, blank=True)


class CustomerAddress(models.Model):
    customer = models.ForeignKey(get_model_name('customer.Customer'))

    name = models.CharField(_('name'), max_length=100)
    address_addition = models.CharField(_('name'), max_length=100)
    street = models.CharField(_('street'), max_length=100)
    city = models.CharField(_('city'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=10)
    country = CountryField(_('country'))

    invoice_address = models.BooleanField(default=False)
