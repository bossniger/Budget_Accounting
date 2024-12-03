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