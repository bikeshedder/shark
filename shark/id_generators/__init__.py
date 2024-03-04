"""
This module contains classes for generating special sequences like
customer numbers that are not plain integer fields.
"""

from datetime import date

from shark.utils.int2base import int2base


class IdGenerator(object):
    # This value should be overwritten by subclasses.
    # Typically an invoice number should not exceed 16 characters as a lot
    # of accounting software assumes this limit. 32 chars also allows the
    # use of UUIDs for an ID field which I assume is a sane maximum length.
    max_length = 32

    def __init__(self, model_class=None, field_name=None):
        self.model_class = model_class
        self.model_class_given = model_class is not None
        self.field_name = field_name
        self.field_name_given = field_name is not None

    def get_queryset(self):
        return self.model_class.objects.all().order_by("-%s" % self.field_name)

    def get_last(self) -> str | None:
        obj = self.get_queryset().first()
        return getattr(obj, self.field_name, None)


class InitialAsNumber(IdGenerator):
    """
    Generate numbers of the format <prefix><initial><n>

    This is typically used in German accounting for customer numbers.
    e.g. "Epic Greatness Corp" might get the customer number "10503".
    "1" being the prefix. "05" for the fifth letter in the alphabet and "03"
    as this company being the third customer with that first lettter in the
    name.

    prefix: defaults to ''
    initial: the first letter of the given initial field as number between
        01 and 26. 00 is used for non-letter initials.
    n: simple counter with n_length characters and to base n_base
    """

    def __init__(
        self,
        model_class=None,
        field_name=None,
        prefix="",
        initial_field_name="name",
        n_length=2,
        n_base=10,
    ):
        super(InitialAsNumber, self).__init__(model_class, field_name)
        self.initial_length = 2
        self.initial_field_name = initial_field_name
        self.n_length = n_length
        self.n_base = n_base
        self.prefix = prefix
        self.format_string = "{prefix}{initial:0>2s}{n:0>%ds}" % (n_length)
        self.max_length = len(prefix) + 2 + n_length

    def format(self, initial_char: str, n: int) -> str:
        return self.format_string.format(
            prefix=self.prefix,
            initial=self.format_initial(initial_char),
            n=self.format_n(n),
        )

    def parse(self, id: str) -> tuple[str, str, int]:
        lp = len(self.prefix)
        prefix, initial_digits, n = id[:lp], id[lp : lp + 2], id[lp + 2 :]
        initial_char = chr(ord("a") + int(initial_digits) - 1)
        return (prefix, initial_char, int(n))

    def format_initial(self, initial_char: str) -> str:
        initial_digits = ord(initial_char.lower()) - ord("a") + 1
        return (
            f"{initial_digits:0>2}"
            if 1 <= initial_digits <= 26
            else "0".zfill(self.n_length)
        )

    def format_n(self, n: int) -> str:
        return int2base(n, self.n_base)

    def get_first(self, initial_char: str) -> str:
        return self.format(initial_char, 1)

    def get_last(self, initial_char: str) -> str:
        start = self.prefix + self.format_initial(initial_char)
        obj = (
            self.get_queryset()
            .filter(**{f"{self.field_name}__istartswith": start})
            .first()
        )
        return getattr(obj, self.field_name, None)

    def next(self, instance=None) -> str:
        initial_char = getattr(instance, self.initial_field_name)[0]
        first_id = self.get_first(initial_char)
        last_id = self.get_last(initial_char)
        if last_id is None:
            return first_id

        (_prefix, _last_initial, last_n) = self.parse(last_id)
        return self.format(initial_char, last_n + 1)


class DaysSinceEpoch(IdGenerator):
    """
    Generate numbers of the format <prefix><days><n>

    prefix: defaults to ''
    days: days since epoch (1970-01-01)
    n: simple counter with n_length characters and to base n_base
    """

    def __init__(
        self,
        model_class=None,
        field_name=None,
        prefix="",
        epoch=date(1970, 1, 1),
        days_length=5,
        days_base=10,
        n_length=3,
        n_base=10,
    ):
        super(DaysSinceEpoch, self).__init__(model_class, field_name)
        self.days_length = days_length
        self.days_base = days_base
        self.prefix = prefix
        self.n_length = n_length
        self.n_base = n_base
        self.epoch = epoch
        self.format_string = "{prefix}{days:0>%ds}{n:0>%ds}" % (days_length, n_length)
        self.max_length = len(prefix) + days_length + n_length

    def format(self, days: int, n: int) -> str:
        return self.format_string.format(
            prefix=self.prefix, days=self.format_days(days), n=self.format_n(n)
        )

    def format_days(self, days: int) -> str:
        return int2base(days, self.days_base)

    def format_n(self, n: int) -> str:
        return int2base(n, self.n_base)

    def parse(self, id: str):
        lp = len(self.prefix)
        ld = self.days_length
        return (
            id[:lp],
            int(id[lp : lp + ld], self.days_base),
            int(id[lp + ld :], self.n_base),
        )

    def get_start(self, today=None) -> str:
        today = today or date.today()
        days = (today - self.epoch).days
        return self.format(days, 0)

    def next(self, instance=None, today=None) -> str:
        start = self.get_start(today)
        last = self.get_last()
        if last is None or start > last:
            return start

        (_prefix, days, last_n) = self.parse(last)
        return self.format(days, last_n + 1)


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
        self.year_customer_format_string = (
            "{prefix}{year:04d}{separator1}" "{customer_number}{separator2}"
        )
        self.format_string = self.year_customer_format_string + "{n:0>%ds}" % n_length
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
        prefix = self.year_customer_format_string.format(
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
    e.g. EXAMPLE-2012-01

    prefix: defaults to ''
    separator1: defaults to '-'
    separator2: defaults to '-', optional
    n: simple counter with n_length characters to the base n_base
    """

    def __init__(
        self,
        model_class=None,
        field_name=None,
        prefix="",
        customer_number_length=20,
        separator1="-",
        year_length=4,
        separator2="-",
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
        self.customer_year_format_string = (
            "{prefix}{customer_number}{separator1}"
            "{year:0>%ds}{separator2}" % year_length
        )
        self.format_string = self.customer_year_format_string + "{n:0>%ds}" % n_length
        self.max_length = (
            len(prefix)
            + len(separator1)
            + 4
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

    def format_year(self, year) -> str:
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
        prefix = self.customer_year_format_string.format(
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
        obj = self.get_queryset(customer, today)[:1].get()
        return getattr(obj, self.field_name)
