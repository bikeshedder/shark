from django.conf import settings
from django.urls import include, path

from . import views

app_name = 'accounting'
urlpatterns = [
    path(r'book-incoming-invoice/', views.book_incoming_invoice, 'book_incoming_invoice'),
]
