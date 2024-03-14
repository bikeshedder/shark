from django.http import HttpRequest
from django.shortcuts import render


def index(request: HttpRequest, tenant_name: str):
    return render(request, "tenant/index.html", {"tenant": request.tenant})
