from .models import Tenant


def add_tenant(get_response):
    def middleware(request):
        # TODO: for simplicity reasons hard-coded
        # This is assuming that a single tenant is using the system
        # Needs to be changed for multi-tenancy
        request.tenant = Tenant.objects.first()
        response = get_response(request)

        return response

    return middleware
