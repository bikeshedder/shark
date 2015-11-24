from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^directdebitbatch/(?P<pk>[^/]+)/sepa\.xml$', 'shark.sepa.admin_views.sepa_xml',
            name='directdebitbatch_sepaxml'),
)
