"""Budgets app — Serializers for Budget and SavingsGoal."""

from rest_framework import serializers
from .models import Budget, SavingsGoal


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name', read_only=True, default='Overall'
    )

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'limit_amount',
            'period', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SavingsGoalSerializer(serializers.ModelSerializer):
    fill_state = serializers.CharField(read_only=True)
    fill_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'name', 'target_amount', 'current_amount',
            'target_date', 'status',
            'fill_state', 'fill_percentage',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'current_amount', 'fill_state',
                            'fill_percentage', 'created_at', 'updated_at']


class SavingsDepositSerializer(serializers.Serializer):
    """For the PUT /savings/{id}/deposit/ endpoint."""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be positive.")
        return value
