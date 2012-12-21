from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^invoiceitem/invoice/', 'shark.billing.admin_views.invoice',
            name='invoiceitem_invoice'),
    url(r'^invoice/(.*)\.pdf$', 'shark.billing.admin_views.invoice_pdf',
            name='invoice_pdf'),
)
