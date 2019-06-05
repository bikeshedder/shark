import unicodecsv as csv

from django import forms
from django.forms.utils import ErrorList
from django.utils.html import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy

from shark.billing.models import InvoiceItem
from shark.customer.models import Customer


class ItemForm(forms.ModelForm):
    customer_number = forms.CharField(max_length=Customer._meta.get_field('number').max_length)

    class Meta:
        model = InvoiceItem
        fields = ['customer_number', 'quantity', 'sku', 'text',
                'begin', 'end', 'price', 'unit', 'discount', 'vat_rate']

    def resolve_customer(self, customer_dict):
        # mark item form errnous if customer does not exist
        customer_number = self.cleaned_data['customer_number']
        customer = customer_dict[customer_number]
        if not customer:
            self.errors.setdefault('customer_number', ErrorList())
            self.errors['customer_number'].append(
                    ugettext('Customer does not exist.'))
        self.cleaned_data['customer'] = customer

    def save(self, commit=True):
        item = super(ItemForm, self).save(commit=False)
        item.customer = self.cleaned_data['customer']
        if commit:
            item.save()
        return item


class ImportItemsForm(forms.Form):
    file = forms.FileField(
            help_text=ugettext_lazy(
                'Please specify a CSV file to be imported. '
                'The following fields are supported:'))
    delimiter = forms.ChoiceField(
            choices=(
                (',', ', (LibreOffice)'),
                (';', '; (Excel)')
            ))
    encoding = forms.ChoiceField(
            choices=(
                ('utf-8', 'utf-8 (LibreOffice)'),
                ('latin1', 'latin1 (Excel)')
            ))

    def __init__(self, *args, **kwargs):
        super(ImportItemsForm, self).__init__(*args, **kwargs)
        file_field = self.fields['file']
        file_field.help_text = format_lazy('{} {}',
                file_field.help_text,
                ', '.join(ItemForm._meta.fields))

    def clean(self):
        super(ImportItemsForm, self).clean()
        if 'file' not in self.cleaned_data or \
                'delimiter' not in self.cleaned_data or \
                'encoding' not in self.cleaned_data:
            return
        item_forms = []
        errnous_rows = []
        class Dialect(csv.excel):
            delimiter = str(self.cleaned_data['delimiter'])
        reader = csv.DictReader(self.cleaned_data['file'],
                dialect=Dialect, encoding=self.cleaned_data['encoding'])
        customer_dict = {}
        # create item forms
        for row, data in enumerate(reader, 2):
            for field_name in ItemForm._meta.fields:
                field_value = data.get(field_name, '')
                if field_value == '':
                    try:
                        field = ItemForm.base_fields[field_name]
                    except KeyError:
                        continue
                    data[field_name] = field.initial
            item_form = ItemForm(data)
            item_forms.append((row, item_form))
            # get customer numbers from all rows
            if item_form.is_valid() and 'customer_number' in item_form.cleaned_data:
                customer_number = item_form.cleaned_data['customer_number']
                customer_dict[customer_number] = None
        # load all customers
        for customer in Customer.objects.filter(number__in=customer_dict.keys()):
            customer_dict[customer.number] = customer
        # prepare list of errnous rows
        for row, item_form in item_forms:
            if item_form.is_valid() and 'customer_number' in item_form.cleaned_data:
                # resolve customer
                item_form.resolve_customer(customer_dict)
            if not item_form.is_valid():
                errnous_rows.append((row, item_form.errors))
        # prepare error message for rows
        if errnous_rows:
            self.errnous_rows = errnous_rows
            errors = self.errors.setdefault('file', ErrorList())
            for row, errnous_fields in errnous_rows:
                row_errors = []
                for field_name, field_errors in errnous_fields.items():
                    row_errors.append('<li>%s: %s</li>' % (
                        field_name, ' '.join(field_errors)))
                errors.append(mark_safe('%s %d:<ul>%s</ul>' % (
                    ugettext('Line'), row, ''.join(row_errors))))
        else:
            self.cleaned_data['items'] = [
                    item_form.save(commit=False)
                    for row, item_form in item_forms]
        return self.cleaned_data
