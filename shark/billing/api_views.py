from rest_framework import generics

from . import api_serializers as serializers
from . import models


class InvoiceList(generics.ListAPIView):
    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceListSerializer


class InvoiceCreate(generics.CreateAPIView):
    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceCreateSerializer


class InvoiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Invoice.objects.all()
    serializer_class = serializers.InvoiceDetailSerializer
