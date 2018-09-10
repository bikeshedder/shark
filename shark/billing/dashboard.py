# -*- coding: UTF-8 -*-

from datetime import date
from datetime import timedelta

from admin_tools.dashboard.modules import DashboardModule
from django.conf import settings
from django.db.models import Sum
from django.urls import reverse
from django.utils.translation import ugettext as _

from shark.billing.models import Invoice, InvoiceItem


class UnpaidInvoicesDashboardModule(DashboardModule):

    def __init__(self, **kwargs):
        super(UnpaidInvoicesDashboardModule, self).__init__(**kwargs)

        self.template = kwargs.get('template', 'billing/dashboard/unpaid-invoices.html')
        self.display = kwargs.get('display', 'tabs')
        self.layout = kwargs.get('layout', 'stacked')
        self.title = kwargs.get('title', _('Unpaid invoices'))

        self.is_empty = False

        today = date.today()
        two_weeks_ago = today - timedelta(days=14)
        thirty_days_ago = today - timedelta(days=30)

        admin_url = reverse('admin:%s_changelist' % settings.SHARK['MODELS']['billing.Invoice'].lower().replace('.', '_'))
        def get_admin_url(**kwargs):
            kwargs.setdefault('paid__isnull', True)
            return '%s?%s' % (admin_url, '&'.join('%s=%s' % item for item in kwargs.items()))

        unpaid = Invoice.objects.filter(paid__isnull=True)
        unpaid_lt14d = unpaid.filter(created__gt=two_weeks_ago)
        unpaid_gt14d = unpaid.filter(created__lte=two_weeks_ago).filter(created__gt=thirty_days_ago)
        unpaid_gt30d = unpaid.filter(created__lte=thirty_days_ago)

        self.unpaid = {
            'lt14d': {
                'count': unpaid_lt14d.count(),
                'url': get_admin_url(created__gt=two_weeks_ago),
            },
            'gt14d': {
                'count': unpaid_gt14d.count(),
                'url': get_admin_url(created__lte=two_weeks_ago, created__gt=thirty_days_ago),
            },
            'gt30d': {
                'count': unpaid_gt30d.count(),
                'url': get_admin_url(created__lte=thirty_days_ago),
            },
            'total': {
                'count': unpaid.count(),
                'url': get_admin_url(),
            }
        }


class LooseItemsDashboardModule(DashboardModule):

    def __init__(self, **kwargs):
        super(LooseItemsDashboardModule, self).__init__(**kwargs)

        self.template = kwargs.get('template', 'billing/dashboard/loose-items.html')
        self.display = kwargs.get('display', 'tabs')
        self.layout = kwargs.get('layout', 'stacked')
        self.title = kwargs.get('title', _('Loose invoice items'))

        self.is_empty = False

        self.items = InvoiceItem.objects.filter(invoice__isnull=True)
        self.item_count = self.items.count()
        self.list_url = reverse('admin:%s_changelist' % settings.SHARK['MODELS']['billing.InvoiceItem'].lower().replace('.', '_')) \
                + '?invoice__isnull=True'
        # XXX disabled for now
        #self.invoice_url = reverse('billing_admin:invoiceitem_invoice')
