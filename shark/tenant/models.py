from django.db import models

from shark.base.models import BaseModel
from shark.utils.fields import AddressField


class Tenant(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    address = AddressField()

    def __str__(self):
        return self.name
