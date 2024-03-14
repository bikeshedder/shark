from django.http import HttpRequest
from django.shortcuts import render


def index(request: HttpRequest, tenant_name: str, project_pk: int):
    return render(request, "project/index.html", {"tenant": request.tenant})
