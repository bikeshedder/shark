'''
This module contains classes for generating special sequences like
customer numbers that are not plain integer fields.
'''

from datetime import date

from shark.utils.int2base import int2base


class IdGenerator(object):
    '''
    This is just an interface class and does not contain any implementation.
    '''

    def __init__(self, model_class, id_field='id'):
        self.model_class = model_class
        self.id_field = id_field

    def get_queryset(self):
        return self.model_class.objects.all() \
                .order_by('-%s' % self.id_field)

    def get_last(self):
        obj = self.get_queryset()[:1].get()
        return getattr(obj, self.id_field)


class DaysSinceEpoch(IdGenerator):
    '''
    Generate numbers of the format <prefix><days><n>

    prefix: defaults to ''
    days: days since epoch (1970-01-01)
    n: simple counter with n_length characters and to base n_base
    '''

    def __init__(self, model_class, id_field='id', prefix='',
            epoch=date(1970, 1, 1), days_length=5, days_base=10,
            n_length=3, n_base=10):
        super(DaysSinceEpoch, self).__init__(model_class, id_field)
        self.days_length = days_length
        self.days_base = days_base
        self.prefix = prefix
        self.n_length = n_length
        self.n_base = n_base
        self.epoch = epoch
        self.format_string = u'{}{:>0%ds}{:>0%ds}' % (days_length, n_length)

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
