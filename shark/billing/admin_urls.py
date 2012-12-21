from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^invoiceitem/invoice/', 'shark.billing.admin_views.invoice',
        name='invoiceitem_invoice'),
)
