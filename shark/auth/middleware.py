from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

LOGIN_REQUIRED_EXEMPT_ROUTES = settings.LOGIN_REQUIRED_EXEMPT_ROUTES


def login_required(get_response):
    def middleware(request):
        if request.user.is_authenticated or any(
            map(
                lambda route: request.path.startswith(route),
                LOGIN_REQUIRED_EXEMPT_ROUTES,
            )
        ):
            response = get_response(request)

            return response

        query = request.GET.urlencode()
        next = f"?next={request.path}" + f"?{query}" if query else ""
        return redirect(reverse("login") + next)

    return middleware
