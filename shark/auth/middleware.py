from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

LOGIN_REQUIRED_ROUTES = getattr(settings, "LOGIN_REQUIRED_ROUTES", [])


def login_required(get_response):
    def middleware(request):
        if not request.user.is_authenticated and any(
            map(
                lambda route: request.path.startswith(route),
                LOGIN_REQUIRED_ROUTES,
            )
        ):
            query = request.GET.urlencode()
            next = f"?next={request.path}" + (f"?{query}" if query else "")
            return redirect(reverse("login") + next)

        response = get_response(request)

        return response

    return middleware
