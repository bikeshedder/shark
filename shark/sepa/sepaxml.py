from dataclasses import dataclass, field
from decimal import Decimal

from django.template.loader import render_to_string

from shark.utils.dataclass import Conversion


@dataclass(kw_only=True)
class Transaction:
    debitor_name: str
    debitor_country: str
    debitor_bic: str
    debitor_iban: str
    reference: str
    amount: Decimal = Conversion(Decimal)
    mandate_id: str
    mandate_date: str


@dataclass(kw_only=True)
class DirectDebit:
    id: str
    creditor_id: str
    creditor_name: str
    creditor_country: str
    creditor_iban: str
    creditor_bic: str
    due_date: str
    mandate_type: str = "CORE"
    sequence_type: str = "FRST"
    transactions: list[Transaction] = field(default_factory=list)
    batch_booking: bool = False

    def __post_init__(self):
        from . import models

        assert self.mandate_type in models.DirectDebitMandate.Type.values
        assert self.sequence_type in models.DirectDebitBatch.SequenceType.values

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    @property
    def control_sum(self):
        return sum(txn.amount for txn in self.transactions)

    def render_xml(self):
        """
        Create SEPA XML document according to ISO20222.
        """
        return render_to_string("sepa/direct_debit.xml", {"dd": self})
