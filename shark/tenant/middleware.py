from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from .models import Tenant, TenantMember


def add_tenant(get_response):
    def middleware(request: HttpRequest):
        if request.user.is_authenticated:
            tenant = None
            if request.path.startswith("/admin"):
                # TODO: current assumption: admin is being used with a single tenant
                tenant = Tenant.objects.first()
            elif request.path.startswith("/app/") and request.path != "/app/":
                # path is /app/tenant_name/....
                # we split the tenant_name
                tenant_name = request.path.split("/")[2]
                tenant = get_object_or_404(
                    Tenant.objects.filter(name__iexact=tenant_name)
                )

            if not request.user.is_superuser and tenant:
                get_object_or_404(TenantMember, user=request.user, tenant=tenant)
            request.tenant = tenant

        response = get_response(request)

        return response

    return middleware
