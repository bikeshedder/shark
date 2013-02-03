from django.conf.urls import patterns, url

urlpatterns = patterns('',
# disabled for now
#    url(r'^invoiceitem/invoice/', 'shark.billing.admin_views.invoice',
#            name='invoiceitem_invoice'),
    url(r'^invoiceitem/import/', 'shark.billing.admin_views.import_items',
            name='import_items'),
    url(r'^invoice/(.*)\.pdf$', 'shark.billing.admin_views.invoice_pdf',
            name='invoice_pdf'),
)
