from django.db import models

class Vendor(models.Model):
    slug = models.SlugField(max_length=20, unique=True)
    name = models.CharField(max_length=50, unique=True)
