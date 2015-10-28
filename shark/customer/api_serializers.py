from rest_framework import serializers

from shark import get_model


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_model('customer.Customer')
        fields = ('number', 'address', 'language', 'created', 'updated')
