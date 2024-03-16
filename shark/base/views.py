from django.http import HttpRequest
from django.shortcuts import render

from shark.tenant.models import Member


def index(request: HttpRequest):
    # Query all tenants that the user has access to
    member_rows = Member.objects.filter(user=request.user)
    tenants = [entry.tenant for entry in member_rows]
    return render(request, "base/index.html", {"tenants": tenants})
