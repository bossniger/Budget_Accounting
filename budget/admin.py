from django.contrib import admin
from budget.models import *


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    pass


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'start_date', 'end_date')
    list_filter = ('user', 'category')
    search_fields = ('category__name', 'user__username')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass
