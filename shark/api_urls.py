from django.conf import settings
from django.urls import include, path

app_name = 'api'
urlpatterns = [
    path('billing/', include('shark.billing.api_urls', namespace='billing')),
]
