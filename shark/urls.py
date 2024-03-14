"""
URL configuration for shark project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("", lambda request: redirect("app/")),
    path("app/", include("shark.base.urls")),
    path(
        "app/<str:tenant_name>/",
        include(
            [
                path("", include("shark.tenant.urls")),
                path(
                    "<int:project_pk>/",
                    include(
                        [
                            path("", include("shark.project.urls")),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path("auth/", include("shark.auth.urls")),
    path("admin/", include("shark.admin_urls")),
    path("api/", include("shark.api_urls")),
    path("grappelli/", include("grappelli.urls")),
    path("grappelli-docs/", include("grappelli.urls_docs")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
