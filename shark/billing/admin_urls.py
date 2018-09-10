from django.urls import path

from . import admin_views as views


app_name = 'billing'
urlpatterns = [
# disabled for now
#    path('invoiceitem/invoice/', 'shark.billing.admin_views.invoice',
#            name='invoiceitem_invoice'),
    path('invoiceitem/import/', views.import_items,
            name='import_items'),
    path('invoice/<number>.pdf', views.invoice_pdf,
            name='invoice_pdf'),
    path('correction/<number>.pdf', views.correction_pdf,
            name='correction_pdf'),
]
