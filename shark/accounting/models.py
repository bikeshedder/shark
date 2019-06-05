from django.db import models


class Account(models.Model):
    name = models.CharField(max_lenght=50)


class Booking(models.Model):
    source = models.ForeignKey('accounting.Account', on_delete=models.CASCADE)
    target = models.ForeignKey('accounting.Account', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    text = models.CharField(max_length=200)
    # booking specific data (e.g. link to article, contract, etc.)
    reference = models.TextField()
