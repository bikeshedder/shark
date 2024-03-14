from django.http import HttpRequest
from django.shortcuts import render


def index(request: HttpRequest):
    return render(request, "tenant/index.html", {"tenant": request.tenant})
