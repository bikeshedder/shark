from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("billing/", include("shark.billing.admin_urls", namespace="billing_admin")),
    path("sepa/", include("shark.sepa.admin_urls", namespace="sepa_admin")),
    path(
        "customer",
        include("shark.customer.admin_urls", namespace="customer_admin"),
    ),
    path("", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns.append(path("doc/", include("django.contrib.admindocs.urls")))
