from decimal import Decimal

from django.conf import settings
from django.template.loader import render_to_string


class DirectDebit(object):

    def __init__(self, **kwargs):
        def kwargs_get(name):
            '''Get SEPA creditor information from kwargs and fallback
            to SEPA_<ARGUMENT_NAME>.'''
            try:
                return kwargs[name]
            except KeyError:
                return getattr(settings, 'SEPA_%s' % name.upper())
        self.id = kwargs['id']
        self.creditor_id = kwargs_get('creditor_id')
        self.creditor_name = kwargs_get('creditor_name')
        self.creditor_country = kwargs_get('creditor_country')
        self.creditor_iban = kwargs_get('creditor_iban')
        self.creditor_bic = kwargs_get('creditor_bic')
        self.due_date = kwargs_get('due_date')
        self.mandate_type = kwargs.get('mandate_type', 'CORE')
        # B2B = without revocation for preauthorized payments
        assert self.mandate_type in ('CORE', 'COR1', 'B2B')
        self.sequence_type = kwargs.get('sequence_type', 'FRST')
        assert self.sequence_type in ('FRST', 'RCUR')
        self.transactions = list(kwargs.get('transactions', []))
        self.batch_booking = kwargs.get('batch_booking', False)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    @property
    def control_sum(self):
        return sum(txn.amount for txn in self.transactions)

    def render_xml(self):
        '''
        Create SEPA XML document according to ISO20222.
        '''
        return render_to_string('sepa/direct_debit.xml', {
            'dd': self
        })


class Transaction(object):

    def __init__(self, debitor_name, debitor_country, debitor_bic, debitor_iban,
            reference, amount, mandate_id, mandate_date):
        self.debitor_name = debitor_name
        self.debitor_country = debitor_country
        self.debitor_iban = debitor_iban
        self.debitor_bic = debitor_bic
        self.reference = reference
        self.amount = Decimal(amount)
        self.mandate_id = mandate_id
        self.mandate_date = mandate_date
