"""
This module contains classes for generating special sequences like
customer numbers that are not plain integer fields.
"""

from datetime import date

from shark.utils.int2base import int2base

from .models import IdGenerator


class YearCustomerN(IdGenerator):
    """
    Generate numbers of the format
    <prefix><year><separator1><customer_number><separator2><n>
    e.g. 2012-EXAMPLE-01

    prefix: defaults to ''
    separator1: defaults to '-'
    separator2: defaults to '-'
    n: simple counter with n_length characters to the base n_base
    """

    def __init__(
        self,
        model_class=None,
        field_name=None,
        prefix="",
        separator1="-",
        separator2="-",
        customer_number_length=20,
        n_length=2,
        n_base=10,
    ):
        # FIXME Is there a way to figure out the customer number length
        #       automatically?
        super(YearCustomerN, self).__init__(model_class, field_name)
        self.prefix = prefix
        self.separator1 = separator1
        self.separator2 = separator2
        self.n_length = n_length
        self.n_base = n_base
        # <prefix><year><separator1><customer_number><separator2><n>
        self.format_string_year_customer = (
            "{prefix}{year:04d}{separator1}" "{customer_number}{separator2}"
        )
        self.format_string = self.format_string_year_customer + "{n:0>%ds}" % n_length
        self.max_length = (
            len(prefix)
            + len(separator1)
            + 4
            + customer_number_length
            + len(separator2)
            + n_length
        )

    def format(self, year: int, customer_number: str, n: int) -> str:
        return self.format_string.format(
            prefix=self.prefix,
            year=year,
            separator1=self.separator1,
            separator2=self.separator2,
            customer_number=customer_number,
            n=self.format_n(n),
        )

    def format_n(self, n: int) -> str:
        return int2base(n, self.n_base)

    def parse(self, id: str) -> tuple[int, str, int]:
        lp = len(self.prefix)
        _prefix, rest = id[:lp], id[lp:]
        year, rest = rest.split(self.separator1, 1)
        year = int(year)
        customer_number, n = rest.rsplit(self.separator2, 1)
        n = int(n, self.n_base)
        return (year, customer_number, n)

    def get_start(self, customer, today=None) -> str:
        today = today or date.today()
        return self.format(today.year, customer.number, 1)

    def next(self, instance, today=None) -> str:
        customer = instance.customer
        today = today or date.today()
        start = self.get_start(customer, today)
        last = self.get_last(customer, today)
        if last is None or start > last:
            return start

        (year, customer_number, last_n) = self.parse(last)
        return self.format(year, customer_number, last_n + 1)

    def get_queryset(self, customer, today):
        prefix = self.format_string_year_customer.format(
            prefix=self.prefix,
            year=today.year,
            separator1=self.separator1,
            separator2=self.separator2,
            customer_number=customer.number,
        )
        return (
            self.model_class.objects.all()
            .filter(**{("%s__startswith" % self.field_name): prefix})
            .order_by("-%s" % self.field_name)
        )

    def get_last(self, customer, today) -> str:
        obj = self.get_queryset(customer, today).first()
        return getattr(obj, self.field_name, None)


class CustomerYearN(IdGenerator):
    """
    Generate numbers of the format
    <prefix><customer_number><separator1><year><separator2><n>
    e.g. EXAMPLE-2401

    prefix: defaults to ''
    separator1: defaults to '-'
    year_length: defaults to 2 (24 instead of 2024)
    separator2: defaults to '', optional
    n: simple counter with n_length characters to the base n_base
    """

    def __init__(
        self,
        model_class=None,
        field_name=None,
        prefix="",
        customer_number_length=20,
        separator1="-",
        year_length=2,
        separator2="",
        n_length=2,
        n_base=10,
    ):
        super(CustomerYearN, self).__init__(model_class, field_name)
        self.prefix = prefix
        self.separator1 = separator1
        self.year_length = year_length
        self.separator2 = separator2
        self.n_length = n_length
        self.n_base = n_base
        # <prefix><year><separator1><customer_number><separator2><n>
        self.format_string_customer_year = "{prefix}{customer_number}{separator1}"
        self.format_string_customer_year = (
            self.format_string_customer_year + "{year:%d}{separator2}" % year_length
        )
        self.format_string = self.format_string_customer_year + "{n:0>%ds}" % n_length
        self.max_length = (
            len(prefix)
            + len(separator1)
            + year_length
            + customer_number_length
            + len(separator2)
            + n_length
        )

    def format(self, customer_number: str, year: int, n: int) -> str:
        return self.format_string.format(
            prefix=self.prefix,
            year=self.format_year(year),
            separator1=self.separator1,
            separator2=self.separator2,
            customer_number=customer_number,
            n=self.format_n(n),
        )

    def format_year(self, year):
        return (("%%0%dd" % self.year_length) % year)[-self.year_length :]

    def format_n(self, n: int) -> str:
        return int2base(n, self.n_base)

    def parse(self, id) -> tuple[str, int, int]:
        lp = len(self.prefix)
        _prefix, rest = id[:lp], id[lp:]
        customer_number, rest = rest.split(self.separator1, 1)
        if self.separator2:
            year, n = rest.rsplit(self.separator2, 1)
        else:
            ly = self.year_length
            year, n = (rest[:ly], rest[ly:])
        year = int(year)
        n = int(n, self.n_base)
        return (customer_number, year, n)

    def get_start(self, customer, today=None) -> str:
        today = today or date.today()
        return self.format(customer.number, today.year, 1)

    def next(self, instance, today=None) -> str:
        customer = instance.customer
        today = today or date.today()
        start = self.get_start(customer, today)
        last = self.get_last(customer, today)
        if last is None or start > last:
            return start

        (customer_number, year, last_n) = self.parse(last)
        return self.format(customer_number, year, last_n + 1)

    def get_queryset(self, customer, today):
        prefix = self.format_string_customer_year.format(
            prefix=self.prefix,
            customer_number=customer.number,
            separator1=self.separator1,
            year=self.format_year(today.year),
            separator2=self.separator2,
        )
        return (
            self.model_class.objects.all()
            .filter(**{("%s__startswith" % self.field_name): prefix})
            .order_by("-%s" % self.field_name)
        )

    def get_last(self, customer, today):
        obj = self.get_queryset(customer, today).first()
        return getattr(obj, self.field_name, None)
