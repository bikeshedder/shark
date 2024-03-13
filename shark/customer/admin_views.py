from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from shark.utils.fields import get_address_fieldlist

from . import models


@require_POST
def get_customer_address(request):
    customer_id = request.POST.get("customer_id")
    address = get_object_or_404(
        models.CustomerAddress, customer=customer_id, billing_address=True
    ).address

    data = {field: getattr(address, field) for field in get_address_fieldlist("")}
    data["country"] = data["country"].code

    return JsonResponse(data)
