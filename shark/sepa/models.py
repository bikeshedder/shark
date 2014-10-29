from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_iban.fields import IBANField
from django_iban.fields import SWIFTBICField

from shark import get_model_name, is_model_overridden
from shark.customer.fields import AddressField


class DirectDebitMandate(models.Model):
    customer = models.ForeignKey(get_model_name('customer.Customer'),
            verbose_name=_('customer'),
            related_name='direct_debit_mandate_set')
    reference = models.CharField(_('mandate reference'),
            max_length=35, unique=True, blank=True)
    address = AddressField(_('address of account holder'))
    iban = IBANField('IBAN',
            help_text='International Bank Account Number')
    bic = SWIFTBICField('BIC',
            help_text='Bank Identifier Code')
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    signed = models.DateField(blank=True, null=True)
    revoked = models.DateField(_('revoked'), blank=True, null=True)
    document = models.ForeignKey('documents.Document',
            verbose_name=_('signed document'),
            blank=True, null=True)

    class Meta:
        verbose_name = _('SEPA direct debit mandate')
        verbose_name_plural = _('SEPA direct debit mandates')


class DirectDebitTransaction(models.Model):
    customer = models.ForeignKey(get_model_name('customer.Customer'),
            verbose_name=_('customer'),
            related_name='direct_debit_transaction_set')
    mandate = models.ForeignKey('sepa.DirectDebitMandate', verbose_name='SEPA DD mandate')
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
    created = models.DateTimeField(_('created'), auto_now_add=True)
    executed = models.DateTimeField(_('executed'))
