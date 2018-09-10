from django.urls import path

from shark.sepa import admin_views

app_name = 'sepa'
urlpatterns = [
    path('directdebitbatch/<pk>/sepa.xml', admin_views.sepa_xml,
            name='directdebitbatch_sepaxml'),
]
