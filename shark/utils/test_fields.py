from django.test import TestCase

from shark.utils.fields import get_address_fieldlist


class TestUtilFields(TestCase):
    def test_address_field_mapping(self):
        self.assertListEqual(
            get_address_fieldlist(""),
            [
                "name",
                "address_addition_1",
                "address_addition_2",
                "street",
                "street_number",
                "city",
                "postal_code",
                "state",
                "country",
            ],
        )
