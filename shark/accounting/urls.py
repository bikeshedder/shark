from django.urls import path

from . import views

app_name = "accounting"
urlpatterns = [
    path(
        "book-incoming-invoice/",
        views.BookIncomingInvoice.as_view(),
        name="book_incoming_invoice",
    ),
]
