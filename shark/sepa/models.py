import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_iban.fields import IBANField
from django_iban.fields import SWIFTBICField
from django_countries.fields import CountryField

from shark import get_model_name, is_model_overridden
from shark.utils.settings import get_settings_value


class DirectDebitMandate(models.Model):
    customer = models.ForeignKey(get_model_name('customer.Customer'),
            verbose_name=_('customer'),
            related_name='direct_debit_mandate_set')
    reference = models.CharField(_('mandate reference'),
            max_length=35, unique=True, blank=True)
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = CountryField(default='DE')
    iban = IBANField('IBAN',
            help_text='International Bank Account Number')
    bic = SWIFTBICField('BIC',
            help_text='Bank Identifier Code')
    bank_name = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    signed = models.DateField(blank=True, null=True)
    revoked = models.DateField(_('revoked'), blank=True, null=True)
    last_used = models.DateField(_('last_used'), blank=True, null=True)
    TYPE_CHOICES = (
        ('CORE', 'CORE'),
        ('COR1', 'COR1'),
        ('B2B', 'B2B'),
    )
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    document = models.ForeignKey('documents.Document',
            verbose_name=_('signed document'),
            blank=True, null=True)

    class Meta:
        verbose_name = _('SEPA direct debit mandate')
        verbose_name_plural = _('SEPA direct debit mandates')

    def address_lines(self):
        return [
            self.name,
            self.street,
            self.postal_code + ' ' + self.city,
            self.get_country_display()
        ]


class DirectDebitTransaction(models.Model):
    customer = models.ForeignKey(get_model_name('customer.Customer'),
            verbose_name=_('customer'),
            related_name='direct_debit_transaction_set')
    mandate = models.ForeignKey('sepa.DirectDebitMandate', verbose_name='SEPA DD mandate')
    reference = models.CharField(max_length=140)
    amount = models.DecimalField(_('amount'),
            max_digits=11, decimal_places=2)
    invoice = models.ForeignKey('billing.Invoice', verbose_name=_('invoice'),
            blank=True, null=True)
    batch = models.ForeignKey('sepa.DirectDebitBatch', verbose_name=_('SEPA DD batch'))
    created = models.DateTimeField(_('created'), auto_now_add=True)


class DirectDebitBatch(models.Model):
    '''
    This model is used to process multiple SEPA DD transactions
    together. This is typically achieved by generating a SEPA XML
    file.
    '''
    uuid = models.UUIDField(_('UUID'), default=uuid.uuid4)
    creditor_id = models.CharField(_('creditor id'), max_length=20,
            default=get_settings_value('SEPA.CREDITOR_ID', ''))
    creditor_name = models.CharField(_('creditor name'), max_length=70,
            default=get_settings_value('SEPA.CREDITOR_NAME', ''))
    creditor_country = models.CharField(_('creditor country'), max_length=2,
            default=get_settings_value('SEPA.CREDITOR_COUNTRY', ''))
    creditor_iban = IBANField(_('creditor IBAN'),
            default=get_settings_value('SEPA.CREDITOR_IBAN', ''))
    creditor_bic = SWIFTBICField(_('creditor BIC'),
            default=get_settings_value('SEPA.CREDITOR_BIC', ''))
    due_date = models.DateTimeField(_('due date'),
            help_text=_('Must be min. 5 TARGET dates in the future for the first transaction and 2 target days in the future for recurring transactions.'))
    mandate_type = models.CharField(_('mandate type'),
            max_length=4, choices=DirectDebitMandate.TYPE_CHOICES)
    SEQUENCE_TYPE_CHOICES = (
        ('FRST', 'FRST'),
        ('RCUR', 'RCUR'),
    )
    sequence_type = models.CharField(_('sequence type'),
            max_length=4, choices=SEQUENCE_TYPE_CHOICES)
    created = models.DateTimeField(_('created'),
            auto_now_add=True)
    executed = models.DateTimeField(_('executed'))
