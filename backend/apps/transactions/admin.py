from django.contrib import admin
from .models import Category, Transaction, IncomeSource, RecurringPattern


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'icon', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'amount', 'category', 'user', 'transaction_date', 'is_deleted']
    list_filter = ['type', 'is_deleted', 'transaction_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'transaction_date'


@admin.register(IncomeSource)
class IncomeSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'amount', 'frequency', 'is_active']
    list_filter = ['frequency', 'is_active']


@admin.register(RecurringPattern)
class RecurringPatternAdmin(admin.ModelAdmin):
    list_display = ['pattern_title', 'user', 'avg_amount', 'frequency', 'occurrence_count']
    list_filter = ['frequency']
