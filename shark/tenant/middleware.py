from django.http import HttpRequest

from .models import Tenant


def add_tenant(get_response):
    def middleware(request: HttpRequest):
        if request.user:
            tenant = None
            if request.path.startswith("/admin"):
                # TODO: current assumption: admin is being used with a single tenant
                tenant = Tenant.objects.first()
            elif request.path.startswith("/app/") and request.path != "/app/":
                # path is /tenant_name/....
                # we split the tenant_name
                tenant_name = request.path.split("/")[1]
                tenant = Tenant.objects.filter(name__iexact=tenant_name).get()

            # TODO: Verify user has access to tenant
            request.tenant = tenant

        response = get_response(request)

        return response

    return middleware
