from django.urls import reverse
from rest_framework import serializers

from shark.customer.api_serializers import CustomerSerializer
from shark.customer.models import Customer

from . import models

class InvoiceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.InvoiceItem
        fields = ('id', 'position', 'quantity', 'sku', 'text',
                'begin', 'end', 'price', 'unit', 'discount',
                'vat_rate')


class InvoiceDetailSerializer(serializers.ModelSerializer):
    #customer = serializers.HyperlinkedRelatedField( # XXX
    items = InvoiceItemSerializer(source='item_set', many=True)

    class Meta:
        model = models.Invoice
        fields = ('id', 'customer', 'type', 'number', 'language',
                'sender', 'recipient', 'net', 'gross', 'created',
                'reminded', 'paid', 'items')
        depth = 1


class CustomerField(serializers.Field):

    def to_representation(self, obj):
        return obj.number

    def to_internal_value(self, data):
        try:
            return Customer.objects.get(number=data)
        except Customer.DoesNotExist:
            raise RuntimeError('No such customer')


class InvoiceListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    customer = CustomerField()

    class Meta:
        model = models.Invoice
        fields = ('id', 'url', 'customer', 'type', 'number',
                'net', 'gross', 'created', 'reminded', 'paid')

    def get_url(self, instance):
        request = self.context['request']
        relative_url = reverse('api:billing:invoice_detail', kwargs={'pk': instance.pk})
        return request.build_absolute_uri(relative_url)


class InvoiceCreateSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = models.Invoice
        fields = ('id', 'customer', 'type', 'number', 'language',
                'sender', 'recipient', 'net', 'gross', 'created',
                'reminded', 'paid', 'items')
        #depth = 1

    def create(self, validated_data):
        # update or create customer
        customer_data = validated_data.pop('customer')
        customer.objects.update_or_create(
            number=customer_data.pop('number'),
            defaults=customer_data
        )
        # create invoice
        invoice = models.Invoice.objects.create(**validated_data)
        # create invoice items
        items_data = validated_data.pop('items')
        for item_data in items_data:
            item = models.InvoiceItem(**item_data)
            invoice.item_set.add(item)
        # recalculate invoice totals
        invoice.recalculate()
        invoice.save()
        return invoice
