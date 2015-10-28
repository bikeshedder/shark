from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^billing/', include('shark.billing.api_urls', namespace='billing')),
)
