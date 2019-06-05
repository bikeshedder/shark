'''
This module contains classes for generating special sequences like
customer numbers that are not plain integer fields.
'''

from copy import copy
from datetime import date

from django.db import models
from django.db.models import signals
from django.utils.functional import curry

from shark.utils.int2base import int2base


class IdGenerator(object):
    # This value should be overwritten by subclasses.
    # Typically an invoice number should not exceed 16 characters as a lot
    # of accounting software assumes this limit. 32 chars also allows the
    # use of UUIDs for an ID field which I assume is a sane maximum length.
    max_length = 32
    '''
    This is just an interface class and does not contain any implementation.
    '''

    def __init__(self, model_class=None, field_name=None):
        self.model_class = model_class
        self.model_class_given = model_class is not None
        self.field_name = field_name
        self.field_name_given = field_name is not None

    def get_queryset(self):
        return self.model_class.objects.all() \
                .order_by('-%s' % self.field_name)

    def get_last(self):
        obj = self.get_queryset()[:1].get()
        return getattr(obj, self.field_name)


class InitialAsNumber(IdGenerator):
    '''
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
    '''
    def __init__(self, model_class=None, field_name=None, prefix='',
            initial_field_name='name',
            n_length=2, n_base=10):
        super(InitialAsNumber, self).__init__(model_class, field_name)
        self.initial_length = 2
        self.initial_field_name = initial_field_name
        self.n_length = n_length
        self.n_base = n_base
        self.format_string = '{prefix}{initial:0>2s}{n:0>%ds}' % (n_length)
        self.max_length = len(prefix) + 2 + n_length

    def format(self, initial, n):
        return self.format_string.format(
            prefix=self.prefix,
            initial=self.format_initial(initial),
            n=self.format_n(n))

    def format_initial(self, s):
        initial = ord(s[0].lower() - ord('a') + 1)
        return f'{initial:0>2s}' if 1 <= initial <= 26 else '00'

    def parse_initial(self, s):
        return chr(ord('a') + int(s) - 1)

    def format_n(self, n):
        return int2base(n, self.n_base)

    def parse(self, s):
        lp = len(self.prefix)
        prefix = s[:lp]
        initial = self.parse_initial(s[lp:lp+2])
        n = s[lp+2:]
        return (prefix, initial, n)

    def get_start(self, initial):
        return self.format(initial, 1)

    def get_last(self, initial):
        start = self.prefix + self.format_initial(initial)
        obj = self.get_queryset() \
                .filter(**{f'{self.field_name}__istartswith': start}) \
                [:1].get()
        return getattr(obj, self.field_name)

    def next(self, instance=None):
        initial = getattr(instance, self.initial_field_name)[0]
        start = self.get_start(initial)
        try:
            last = self.get_last(initial)
            if start > last:
                return start
            (prefix, last_initial, last_n) = self.parse(last)
            return self.format(days, last_n+1)
        except self.model_class.DoesNotExist:
            return start


class DaysSinceEpoch(IdGenerator):
    '''
    Generate numbers of the format <prefix><days><n>

    prefix: defaults to ''
    days: days since epoch (1970-01-01)
    n: simple counter with n_length characters and to base n_base
    '''

    def __init__(self, model_class=None, field_name=None, prefix='',
            epoch=date(1970, 1, 1), days_length=5, days_base=10,
            n_length=3, n_base=10):
        super(DaysSinceEpoch, self).__init__(model_class, field_name)
        self.days_length = days_length
        self.days_base = days_base
        self.prefix = prefix
        self.n_length = n_length
        self.n_base = n_base
        self.epoch = epoch
        self.format_string = '{prefix}{days:0>%ds}{n:0>%ds}' % (
                days_length, n_length)
        self.max_length = len(prefix) + days_length + n_length

    def format(self, days, n):
        return self.format_string.format(
            prefix=self.prefix,
            days=self.format_days(days),
            n=self.format_n(n))

    def format_days(self, days):
        return int2base(days, self.days_base)

    def format_n(self, n):
        return int2base(n, self.n_base)

    def parse(self, s):
        lp = len(self.prefix)
        ld = self.days_length
        return (s[:lp], int(s[lp:lp+ld], self.days_base),
                int(s[lp+ld:], self.n_base))

    def get_start(self, today=None):
        today = today or date.today()
        days = (today - self.epoch).days
        return self.format(days, 0)

    def next(self, instance=None, today=None):
        start = self.get_start(today)
        try:
            last = self.get_last()
            if start > last:
                return start
            (prefix, days, last_n) = self.parse(last)
            return self.format(days, last_n+1)
        except self.model_class.DoesNotExist:
            return start


class YearCustomerN(IdGenerator):
    '''
    Generate numbers of the format
    <prefix><year><separator1><customer_number><separator2><n>
    e.g. 2012-EXAMPLE-01

    prefix: defaults to ''
    separator1: defaults to '-'
    separator2: defaults to '-'
    n: simple counter with n_length characters to the base n_base
    '''

    def __init__(self, model_class=None, field_name=None, prefix='',
            separator1='-', separator2='-', customer_number_length=20, n_length=2, n_base=10):
        # FIXME Is there a way to figure out the customer number length
        #       automatically?
        super(YearCustomerN, self).__init__(model_class, field_name)
        self.prefix = prefix
        self.separator1 = separator1
        self.separator2 = separator2
        self.n_length = n_length
        self.n_base = n_base
        # <prefix><year><separator1><customer_number><separator2><n>
        self.year_customer_format_string = \
                '{prefix}{year:04d}{separator1}' \
                '{customer_number}{separator2}'
        self.format_string = self.year_customer_format_string + \
                '{n:0>%ds}' % n_length
        self.max_length = len(prefix) + len(separator1) + 4 + \
                customer_number_length + len(separator2) + n_length

    def format(self, year, customer_number, n):
        return self.format_string.format(
            prefix=self.prefix,
            year=year,
            separator1=self.separator1,
            separator2=self.separator2,
            customer_number=customer_number,
            n=self.format_n(n))

    def format_n(self, n):
        return int2base(n, self.n_base)

    def parse(self, s):
        lp = len(self.prefix)
        prefix, rest = (s[:lp], s[lp:])
        year, rest = rest.split(self.separator1, 1)
        year = int(year)
        customer_number, n = rest.rsplit(self.separator2, 1)
        n = int(n, self.n_base)
        return (year, customer_number, n)

    def get_start(self, customer, today=None):
        today = today or date.today()
        return self.format(today.year, customer.number, 1)

    def next(self, instance, today=None):
        customer = instance.customer
        today = today or date.today()
        start = self.get_start(customer, today)
        try:
            last = self.get_last(customer, today)
            if start > last:
                return start
            (year, customer_number, last_n) = self.parse(last)
            return self.format(year, customer_number, last_n+1)
        except self.model_class.DoesNotExist:
            return start

    def get_queryset(self, customer, today):
        prefix = self.year_customer_format_string.format(
            prefix=self.prefix,
            year=today.year,
            separator1=self.separator1,
            separator2=self.separator2,
            customer_number=customer.number)
        return self.model_class.objects.all() \
                .filter(**{ ('%s__startswith' % self.field_name): prefix }) \
                .order_by('-%s' % self.field_name)

    def get_last(self, customer, today):
        obj = self.get_queryset(customer, today)[:1].get()
        return getattr(obj, self.field_name)


class CustomerYearN(IdGenerator):
    '''
    Generate numbers of the format
    <prefix><customer_number><separator1><year><separator2><n>
    e.g. EXAMPLE-2012-01

    prefix: defaults to ''
    separator1: defaults to '-'
    separator2: defaults to '-', optional
    n: simple counter with n_length characters to the base n_base
    '''

    def __init__(self, model_class=None, field_name=None, prefix='',
            customer_number_length=20, separator1='-', year_length=4,
            separator2='-', n_length=2, n_base=10):
        super(CustomerYearN, self).__init__(model_class, field_name)
        self.prefix = prefix
        self.separator1 = separator1
        self.year_length = year_length
        self.separator2 = separator2
        self.n_length = n_length
        self.n_base = n_base
        # <prefix><year><separator1><customer_number><separator2><n>
        self.customer_year_format_string = \
                '{prefix}{customer_number}{separator1}' \
                '{year:0>%ds}{separator2}' % year_length
        self.format_string = self.customer_year_format_string + \
                '{n:0>%ds}' % n_length
        self.max_length = len(prefix) + len(separator1) + 4 + \
                customer_number_length + len(separator2) + n_length

    def format(self, customer_number, year, n):
        return self.format_string.format(
            prefix=self.prefix,
            year=self.format_year(year),
            separator1=self.separator1,
            separator2=self.separator2,
            customer_number=customer_number,
            n=self.format_n(n))

    def format_year(self, year):
        return (('%%0%dd' % self.year_length) % year)[-self.year_length:]

    def format_n(self, n):
        return int2base(n, self.n_base)

    def parse(self, s):
        lp = len(self.prefix)
        prefix, rest = (s[:lp], s[lp:])
        customer_number, rest = rest.split(self.separator1, 1)
        if self.separator2:
            year, n = rest.rsplit(self.separator2, 1)
        else:
            ly = self.year_length
            year, n = (rest[:ly], rest[ly:])
        year = int(year)
        n = int(n, self.n_base)
        return (customer_number, year, n)

    def get_start(self, customer, today=None):
        today = today or date.today()
        return self.format(customer.number, today.year, 1)

    def next(self, instance, today=None):
        customer = instance.customer
        today = today or date.today()
        start = self.get_start(customer, today)
        try:
            last = self.get_last(customer, today)
            if start > last:
                return start
            (customer_number, year, last_n) = self.parse(last)
            return self.format(customer_number, year, last_n+1)
        except self.model_class.DoesNotExist:
            return start

    def get_queryset(self, customer, today):
        prefix = self.customer_year_format_string.format(
            prefix=self.prefix,
            customer_number=customer.number,
            separator1=self.separator1,
            year=self.format_year(today.year),
            separator2=self.separator2)
        return self.model_class.objects.all() \
                .filter(**{ ('%s__startswith' % self.field_name): prefix }) \
                .order_by('-%s' % self.field_name)

    def get_last(self, customer, today):
        obj = self.get_queryset(customer, today)[:1].get()
        return getattr(obj, self.field_name)


class IdField(models.CharField):

    def __init__(self, **kwargs):
        self.generator = kwargs.pop('generator', None)
        kwargs.setdefault('max_length', 32)
        if self.generator:
            if self.generator.max_length > kwargs['max_length']:
                raise RuntimeError('The generator is capable of generating IDs exceeding the max_length of this field. Consider using a different generator class or setting a higher max_length value to this field.')
        kwargs.setdefault('blank', True)
        kwargs.setdefault('unique', True)
        super(IdField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name):
        super(IdField, self).contribute_to_class(cls, name)
        if self.generator:
            generator = copy(self.generator)
            if not generator.model_class_given:
                generator.model_class = cls
            if not generator.field_name_given:
                generator.field_name = name
            signals.pre_save.connect(curry(self._pre_save, generator=generator),
                    sender=cls, weak=False)

    # Do not name this method 'pre_save' as it will otherwise be called without
    # the generator argument.
    def _pre_save(self, generator, sender, instance, *args, **kwargs):
        if getattr(instance, self.name, ''):
            # Do not create an ID for objects that already have a value set.
            return
        value = generator.next(instance=instance)
        setattr(instance, self.name, value)
