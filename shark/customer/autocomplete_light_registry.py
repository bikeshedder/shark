import autocomplete_light

from shark import get_model
from shark.customer import models


class CustomerAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['number', 'address']
    model = get_model('customer.Customer')

    def choices_for_request(self):
        if not self.request.user.is_superuser:
            self.choices = self.choices.none()
        return super(CustomerAutocomplete, self).choices_for_request()

    def choice_label(self, instance):
        return u'%s - %s' % (instance.number, ', '.join(instance.address.split('\n')))


autocomplete_light.register(CustomerAutocomplete)