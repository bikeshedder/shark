from datetime import date, timedelta

from django.urls import reverse
from django.utils.translation import gettext as _
from grappelli.dashboard.modules import DashboardModule

from shark.billing.models import Invoice


class UnpaidInvoicesDashboardModule(DashboardModule):
    title = _("Unpaid invoices")
    template = "billing/dashboard/unpaid-invoices.html"

    def is_empty(self):
        return False

    def init_with_context(self, context):
        if self._initialized:
            return

        today = date.today()
        two_weeks_ago = today - timedelta(days=14)
        thirty_days_ago = today - timedelta(days=30)

        admin_url = reverse("admin:billing_invoice_changelist")

        def get_admin_url(**kwargs):
            kwargs.setdefault("paid_at__isnull", True)
            return "%s?%s" % (
                admin_url,
                "&".join("%s=%s" % item for item in kwargs.items()),
            )

        unpaid = Invoice.objects.filter(paid_at__isnull=True)
        unpaid_lt14d = unpaid.filter(created_at__gt=two_weeks_ago)
        unpaid_gt14d = unpaid.filter(created_at__lte=two_weeks_ago).filter(
            created_at__gt=thirty_days_ago
        )
        unpaid_gt30d = unpaid.filter(created_at__lte=thirty_days_ago)

        self.unpaid = {
            "lt14d": {
                "count": unpaid_lt14d.count(),
                "url": get_admin_url(created_at__gt=two_weeks_ago),
            },
            "gt14d": {
                "count": unpaid_gt14d.count(),
                "url": get_admin_url(
                    created_at__lte=two_weeks_ago, created_at__gt=thirty_days_ago
                ),
            },
            "gt30d": {
                "count": unpaid_gt30d.count(),
                "url": get_admin_url(created_at__lte=thirty_days_ago),
            },
            "total": {
                "count": unpaid.count(),
                "url": get_admin_url(),
            },
        }

        self._initialized = True
