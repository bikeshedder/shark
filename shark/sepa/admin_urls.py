from django.conf.urls import url

from shark.sepa import admin_views

urlpatterns = [
    url(r'^directdebitbatch/(?P<pk>[^/]+)/sepa\.xml$', admin_views.sepa_xml,
            name='directdebitbatch_sepaxml'),
]
