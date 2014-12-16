from xml.sax.saxutils import escape

from django.contrib import admin

from shark.customer import models


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['number', 'address_html', 'created']
    list_filter = ['created']
    search_fields = ['number', 'address']
    date_hierarchy = 'created'

    def address_html(self, instance):
        return '<br/>'.join(map(escape, instance.address_lines))
    address_html.allow_tags = True
    address_html.short_description = models.Customer._meta.get_field('address').verbose_name
    address_html.admin_order_field = 'address'


if not models.Customer._meta.abstract:
    admin.site.register(models.Customer, CustomerAdmin)
