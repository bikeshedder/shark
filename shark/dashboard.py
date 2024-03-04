"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'shark.dashboard.CustomIndexDashboard'
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from grappelli.dashboard import Dashboard, modules
from grappelli.dashboard.utils import get_admin_site_name

from shark.billing.dashboard import (
    LooseItemsDashboardModule,
    UnpaidInvoicesDashboardModule,
)


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        self.children.append(
            modules.Group(
                column=1,
                children=[
                    modules.ModelList(
                        _("Applications"),
                        exclude=("django.contrib.*",),
                    ),
                    modules.ModelList(
                        _("Administration"),
                        models=("django.contrib.*",),
                    ),
                ],
            )
        )

        self.children.append(
            modules.Group(
                column=2,
                css_classes=["g-d-12"],
                children=[
                    UnpaidInvoicesDashboardModule(),
                    LooseItemsDashboardModule(),
                    modules.LinkList(
                        title=_("Quick links"),
                        children=[
                            [_("Log out"), reverse("%s:logout" % site_name)],
                        ],
                    ),
                    modules.RecentActions(
                        _("Recent actions"),
                        limit=5,
                    ),
                ],
            )
        )
