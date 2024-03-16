from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from shark.project.models import Project

from .models import Member


def index(request: HttpRequest):
    member = get_object_or_404(Member, tenant=request.tenant, user=request.user)
    if member.role == Member.Role.ADMIN:
        projects = Project.objects.filter(tenant=request.tenant).all()
    else:
        projects = member.projects.all()
    return render(request, "tenant/index.html", {"projects": projects})
