# -*- coding: UTF-8 -*-

from os.path import splitext

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from shark.documents import models


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'title', 'get_extension', 'date', 'get_size', 'mime_type')
    list_display_links = ('get_thumbnail', 'title')
    list_filter = ('date', 'source', 'mime_type', 'tags')
    search_fields = ('title',)

    def get_thumbnail(self, instance):
        if instance.thumbnail_small:
            return format_html('<img src="{}">', instance.thumbnail_small.url)
    get_thumbnail.short_description = _('Thumbnail')

    def get_extension(self, instance):
        fn, ext = splitext(instance.file.name)
        return ext[1:] if ext.startswith('.') else ext
    get_extension.short_description = _('Ext.')

    def get_size(self, instance):
        return filesizeformat(instance.size)
    get_size.short_description = _('Size')
    get_size.admin_order_field = 'size'


admin.site.register(models.Document, DocumentAdmin)
