from django.views.generic import TemplateView


class BookIncomingInvoice(TemplateView):
    pass


book_incoming_invoice = BookIncomingInvoice.as_view()
