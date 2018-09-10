from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views as views


app_name ='billing'
urlpatterns = [
    path(r'invoice/', views.InvoiceList.as_view(), name='invoice_list'),
    path(r'invoice/create/', views.InvoiceCreate.as_view(), name='invoice_create'),
    path(r'invoice/<int:pk>/', views.InvoiceDetail.as_view(), name='invoice_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
