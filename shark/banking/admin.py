from django.contrib import admin

from shark.banking import models


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name',)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'entry_date', 'value_date', 'reference', 'amount', 'debit_credit')
    list_filter = ('account', 'entry_date', 'value_date')
    search_fields = ('reference',)


admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
