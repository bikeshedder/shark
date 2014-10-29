from django.conf import settings
from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^book-incoming-invoice/$', views.book_incoming_invoice, 'book_incoming_invoice'),
)
