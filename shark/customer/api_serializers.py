from rest_framework import serializers

from . import models


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Customer
        fields = ('number', 'address', 'language', 'created', 'updated')
