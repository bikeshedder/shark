# -*- coding: UTF-8 -*-

from datetime import date
from datetime import timedelta

from django.db.models import Sum
from django.conf import settings
from django.utils.translation import ugettext as _

from admin_tools.dashboard.modules import DashboardModule

from webconf.billing.models import Invoice


class InvoicesDashboardModule(DashboardModule):

    def __init__(self, **kwargs):

        super(InvoicesDashboardModule, self).__init__(**kwargs)

        self.template = kwargs.get('template', 'billing/dashboard/invoices.html')
        self.display = kwargs.get('display', 'tabs')
        self.layout = kwargs.get('layout', 'stacked')
        self.title = kwargs.get('title', _('Invoices'))

        self.is_empty = False

        self.today = date.today()
        self.two_weeks_ago = self.today - timedelta(days=14)
        self.thirty_days_ago = self.today - timedelta(days=30)

        unpaid_invoices = Invoice.objects.filter(paid__isnull=True)
        unpaid_invoices_lt14d = unpaid_invoices.filter(created__gt=self.two_weeks_ago)
        unpaid_invoices_gt14d = unpaid_invoices.filter(created__lt=self.two_weeks_ago).filter(created__gte=self.thirty_days_ago)
        unpaid_invoices_gt30d = unpaid_invoices.filter(created__lt=self.thirty_days_ago)

        self.invoices = {
                'unpaid': unpaid_invoices,
                'unpaid_lt14d': unpaid_invoices_lt14d,
                'unpaid_gt14d': unpaid_invoices_gt14d,
                'unpaid_gt30d': unpaid_invoices_gt30d,
                'recently_paid': Invoice.objects.filter(paid__isnull=False).order_by('-paid')[:5]
        }

    def init_with_context(self, context):
        pass
