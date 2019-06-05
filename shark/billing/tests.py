# -*- coding: utf-8 -*-

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Invoice


class AccountTests(APITestCase):

    def test_create_invoice(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api:billing:invoice_create')
        response = self.client.post(url, {
            'customer': {
                #'number': test_customer.number,
                'number': 'TEST',
            },
            'number': 'TEST-0001',
            'items': [
                {
                    "position": 1,
                    "quantity": "100.00",
                    "sku": "",
                    "text": "Waffelhörnchen",
                    "begin": None,
                    "end": "2015-01-01",
                    "price": "0.1",
                    "unit": "m",
                    "discount": "0.00",
                    "vat_rate": 0.19
                }
            ]
        }, format='json')
        print response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check the newly created invoice
        self.assertEqual(Invoice.objects.count(), 1)
        invoice = Invoice.objects.count
        customer = invoice.customer
        self.assertEqual(customer.number, 'TEST')
        self.assertEqual(invoice.number, 'TEST-0001')
        self.assertEqual(Invoice.objects.get().net, Decimal('10.00'))
        self.assertEqual(Invoice.objects.get().gross, Decimal('11.90'))
