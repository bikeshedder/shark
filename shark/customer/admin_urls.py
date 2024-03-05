from django.urls import path

from . import admin_views

app_name = "customer"
urlpatterns = [
    path(
        "get_customer_address/",
        admin_views.get_customer_address,
        name="get_customer_address",
    ),
]
