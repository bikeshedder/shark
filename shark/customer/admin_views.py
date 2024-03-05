from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from . import models


@require_POST
def get_customer_address(request):
    customer_id = request.POST.get("customer_id")
    address = get_object_or_404(
        models.CustomerAddress, customer=customer_id, invoice_address=True
    ).address

    data = {
        "name": address.name,
        "address_addition_1": address.address_addition_1,
        "address_addition_2": address.address_addition_2,
        "street": address.street,
        "street_number": address.street_number,
        "city": address.city,
        "postal_code": address.postal_code,
        "state": address.state,
        "country": address.country.code,
    }
    return JsonResponse(data)
