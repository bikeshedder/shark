"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'shark.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import gettext_lazy as _
from grappelli.dashboard import Dashboard, modules

from shark.billing.dashboard import UnpaidInvoicesDashboardModule
from shark.project.dashboard import ProjectDashboardModule


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        self.children.append(
            modules.Group(
                column=1,
                children=[
                    ProjectDashboardModule(),
                    UnpaidInvoicesDashboardModule(),
                ],
            ),
        )

        self.children.append(
            modules.Group(
                column=2,
                css_classes=["g-d-12"],
                children=[
                    modules.ModelList(
                        _("Applications"),
                    ),
                    modules.RecentActions(
                        _("Recent actions"),
                        limit=5,
                    ),
                ],
            )
        )
