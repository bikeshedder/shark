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
        self.field_name = field_name

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

    def __init__(self, model_class=None, field_name='id', prefix='',
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

    def next(self, today=None):
        start = self.get_start(today)
        try:
            last = self.get_last()
            if start > last:
                return start
            (prefix, days, last_n) = self.parse(last)
            return self.format(days, last_n+1)
        except self.model_class.DoesNotExist:
            return start


class IdField(models.CharField):

    def __init__(self, generator, **kwargs):
        self.generator = generator
        self.name = None
        kwargs.setdefault('max_length', generator.max_length)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('unique', True)
        super(IdField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name):
        super(IdField, self).contribute_to_class(cls, name)
        self.name = name
        generator = copy(self.generator)
        if generator.model_class is None:
            generator.model_class = cls
            generator.field_name = name
        signals.pre_save.connect(curry(self._pre_save, generator=generator),
                sender=cls, weak=False)

    # Do not name this method 'pre_save' as it will otherwise be called without
    # the generator argument.
    def _pre_save(self, generator, sender, instance, *args, **kwargs):
        if getattr(sender, self.name, ''):
            return
        value = generator.next()
        setattr(instance, self.name, value)
