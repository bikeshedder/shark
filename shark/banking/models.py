from django.db import models
from django.utils.translation import ugettext_lazy as _


class Account(models.Model):
    name = models.CharField(_('account name'),
            max_length=50)


class Transaction(models.Model):
    account = models.ForeignKey('banking.Account', on_delete=models.CASCADE)
    entry_date = models.DateField(_('entry date'))
    value_date = models.DateField(_('value date'))
    text_key = models.CharField(max_length=100) # XXX max_length?
    primanota = models.CharField(max_length=100) # XXX max_length?
    account_holder = models.CharField(max_length=100) # XXX max_length?
    account_number = models.CharField(max_length=100) # XXX max_length?
    bank_code = models.CharField(max_length=100) # XXX max_length?
    reference = models.TextField(max_length=100) # XXX max_length?
    currency = models.CharField(max_length=3, default='EUR')
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    debit_credit = models.CharField(max_length=2)
