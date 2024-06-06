from rest_framework import viewsets

from shark.tenant.models import Tenant
from shark.utils.api import HTMXModelViewSet

from .. import models
from . import serializers


class TaskViewSet(HTMXModelViewSet):
    serializer_class = serializers.TaskSerializer
    htmx_templates = {
        "retrieve": {"name": "project/partials/task-edit.html"},
        "create": {"name": "project/partials/task-create.html"},
        "create-success": {"name": "project/partials/task-list-entry.html"},
    }

    def get_queryset(self):
        tenants = Tenant.objects.filter(tenantmember__user=self.request.user)
        return models.Task.objects.filter(project__tenant__in=tenants)


class TaskTimeEntryViewSet(viewsets.ModelViewSet):
    queryset = models.TaskTimeEntry.objects.all()
    serializer_class = serializers.TaskTimeEntrySerializer
