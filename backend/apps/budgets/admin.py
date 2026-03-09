from django.contrib import admin
from .models import Budget, SavingsGoal


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'limit_amount', 'period', 'is_active']
    list_filter = ['period', 'is_active']


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'current_amount', 'target_amount', 'status', 'fill_state']
    list_filter = ['status']
