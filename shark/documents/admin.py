# -*- coding: UTF-8 -*-

from django.contrib import admin

from shark.documents import models


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'size', 'mime_type')
    list_filter = ('date', 'original', 'mime_type', 'tags')
    search_fields = ('title',)


admin.site.register(models.Document, DocumentAdmin)
