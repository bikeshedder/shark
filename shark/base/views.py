from django.http import HttpRequest
from django.shortcuts import render

from shark.tenant.models import TenantMember


def index(request: HttpRequest):
    # Query all tenants that the user has access to
    member_rows = TenantMember.objects.filter(user=request.user)
    return render(
        request, "base/index.html", {"tenants": [row.tenant for row in member_rows]}
    )
