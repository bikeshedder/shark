from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views as views


urlpatterns = [
    url(r'^invoice/$', views.InvoiceList.as_view(), name='invoice_list'),
    url(r'^invoice/create/$', views.InvoiceCreate.as_view(), name='invoice_create'),
    url(r'^invoice/(?P<pk>[0-9]+)/$', views.InvoiceDetail.as_view(), name='invoice_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
