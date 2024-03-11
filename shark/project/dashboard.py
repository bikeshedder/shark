from django.utils.translation import gettext as _
from grappelli.dashboard.modules import DashboardModule

from . import models


class ProjectDashboardModule(DashboardModule):
    title = _("Project management")
    template = "admin/project/dashboard/index.html"

    def is_empty(self):
        return False

    def init_with_context(self, context):
        if self._initialized:
            return

        request = context["request"]
        if hasattr(request, "tenant"):
            self.projects = models.Project.objects.filter(
                tenant=request.tenant, active=True
            )
        else:
            self.projects = []

        self._initialized = True
