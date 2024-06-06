from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from .models import Tenant, TenantMember


def add_tenant(get_response):
    def middleware(request: HttpRequest):
        if request.user.is_authenticated:
            tenant, tenant_member = None, None

            if request.path.startswith("/admin"):
                # TODO: current assumption: admin is being used with a single tenant
                tenant = Tenant.objects.first()

            # The only route that is not guarded with the tenant check
            # is /app/ which is the Tenant selection itself
            elif request.path.startswith("/app/") and request.path != "/app/":
                # path is `/app/<tenant_slug>/....`
                slug = request.path.split("/")[2]
                tenant = get_object_or_404(Tenant.objects.filter(slug=slug))
                tenant_member = get_object_or_404(
                    TenantMember, user=request.user, tenant=tenant
                )

            request.tenant = tenant
            request.tenant_member = tenant_member

        response = get_response(request)

        return response

    return middleware


def remove_tenantname_kwarg(request, view_func, view_args, view_kwargs):
    if "tenant" in view_kwargs:
        del view_kwargs["tenant"]


def remove_tenant_capturing_group(get_response):
    def middleware(request: HttpRequest):
        response = get_response(request)

        return response

    middleware.process_view = remove_tenantname_kwarg
    return middleware
