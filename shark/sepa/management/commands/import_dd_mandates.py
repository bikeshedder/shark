import argparse
from decimal import Decimal
from functools import partial

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
import unicodecsv as csv

from shark.customer.models import Customer
from shark.sepa.models import DirectDebitMandate


class Command(BaseCommand):
    args = '<csv_file>'
    help = 'import questions from CSV file'
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('filename', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        mandates = []
        fh = options['filename']
        reader = csv.DictReader(fh)
        has_error = False
        for row_index, row in enumerate(reader, 1):
            if row.get('#', '') == '#':
                # skip comment rows
                continue
            try:
                customer_number = row['customer_number']
                customer = Customer.objects.get(number=customer_number)
            except Customer.DoesNotExist:
                print('Unknown customer number: ', customer_number)
                continue
            mandate_data = {
                'customer': customer,
                'type': row['type'],
                'name': row['name'],
                'street': row['street'],
                'postal_code': row['postal_code'],
                'city': row['city'],
                'bank_name': row['bank_name'],
                'bic': row['bic'],
                'iban': row['iban'],
                'signed': row['signed'],
                'reference': customer.number + '-M01',
            }
            mandate = DirectDebitMandate(**mandate_data)
            try:
                mandate.clean_fields()
                mandate.clean()
            except ValidationError as e:
                has_error = True
                print('Errors in row %d:' % (row_index+1))
                for error in e:
                    print('  - %s: %s' % error)
                #print('Invalid row[%d]: %s' % (row_index, e))
            mandates.append(mandate_data)
        if has_error:
            print('Error(s) in document found. Aborting.')
            return
        for mandate_data in mandates:
            DirectDebitMandate.objects.get_or_create(**mandate_data)
            customer = mandate_data['customer']
            customer.payment_type = 'direct_debit'
            customer.save()
