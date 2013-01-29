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
    max_length = 20 # this value should be overwritten by subclasses
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
        self.format_string = u'{}{:>0%ds}{:>0%ds}' % (days_length, n_length)
        self.max_length = len(prefix) + days_length + n_length

    def format(self, days, n):
        return self.format_string.format(self.prefix,
                self.format_days(days), self.format_n(n))

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
    <prefix><year><separator><customer_number><separator><n>
    e.g. 2012-EXAMPLE-01

    prefix: defaults to ''
    separator: defaults to '-'
    n: simple counter with n_length characters to the base n_base
    '''

    def __init__(self, model_class=None, field_name=None, prefix='',
            separator='-', customer_number_length=20, n_length=2, n_base=10):
        # FIXME Is there a way to figure out the customer number length
        #       automatically?
        super(YearCustomerN, self).__init__(model_class, field_name)
        self.prefix = prefix
        self.separator = separator
        self.n_length = n_length
        self.n_base = n_base
        # <prefix><year><separator><customer_number><separator><n>
        self.format_string = u'{}{:>04d}{}{}{}{:>0%ds}' % n_length
        self.max_length = len(prefix) + len(separator) + 4 + \
                customer_number_length + len(separator) + n_length

    def format(self, year, customer_number, n):
        return self.format_string.format(self.prefix,
                year, self.separator, customer_number,
                self.separator, self.format_n(n))

    def format_n(self, n):
        return int2base(n, self.n_base)

    def parse(self, s):
        lp = len(self.prefix)
        ls = len(self.separator)
        prefix, rest = (s[:lp], s[lp:])
        year, rest = rest.split(self.separator, 1)
        year = int(year)
        customer_number, n = rest.rsplit(self.separator, 1)
        n = int(n, self.n_base)
        return (year, customer_number, n)

    def get_start(self, customer, today=None):
        today = today or date.today()
        return self.format(today.year, customer.number, 1)

    def next(self, instance, today=None):
        customer = instance
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
        prefix = u'%s%s' % (self.prefix, today.year)
        return self.model_class.objects.all() \
                .filter(**{ ('%s__startswith' % self.field_name): prefix }) \
                .order_by('-%s' % self.field_name)

    def get_last(self, customer, today):
        obj = self.get_queryset(customer, today)[:1].get()
        return getattr(obj, self.field_name)


class IdField(models.CharField):

    def __init__(self, generator, **kwargs):
        self.generator = generator
        kwargs.setdefault('max_length', generator.max_length)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('unique', True)
        super(IdField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name):
        super(IdField, self).contribute_to_class(cls, name)
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
