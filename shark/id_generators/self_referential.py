from datetime import date

from shark.utils.int2base import int2base

from .models import IdGenerator


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
        prefix="T",  # TODO: To edit options, need to store more info in DB
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
        return f"{initial_digits:0>2}" if 1 <= initial_digits <= 26 else "00"

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
