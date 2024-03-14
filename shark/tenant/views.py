from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from shark.project.models import Project

from .models import TenantMember


def index(request: HttpRequest):
    member = get_object_or_404(TenantMember, tenant=request.tenant, user=request.user)
    if member.role == TenantMember.Role.ADMIN:
        projects = Project.objects.filter(tenant=request.tenant).all()
    else:
        projects = member.projects.all()
    return render(request, "tenant/index.html", {"projects": projects})
