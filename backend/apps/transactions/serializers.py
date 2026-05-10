"""Transactions app — Serializers for Transaction, Category, IncomeSource."""

from rest_framework import serializers
from .models import Category, Transaction, IncomeSource, RecurringPattern


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'color_hex', 'is_default', 'created_at']
        read_only_fields = ['id', 'is_default', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'title', 'description', 'amount',
            'transaction_date', 'category', 'category_detail',
            'auto_category', 'category_confidence',
            'is_synced', 'device_id',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'auto_category', 'category_confidence',
            'is_synced', 'created_at', 'updated_at',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Lighter serializer for creating transactions."""

    class Meta:
        model = Transaction
        fields = [
            'type', 'title', 'description', 'amount',
            'transaction_date', 'category', 'device_id',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        fields = [
            'id', 'name', 'amount', 'frequency',
            'next_expected', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecurringPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringPattern
        fields = [
            'id', 'pattern_title', 'avg_amount', 'frequency',
            'occurrence_count', 'first_seen', 'last_seen',
            'user_acknowledged',
        ]
        read_only_fields = ['id', 'pattern_title', 'avg_amount', 'frequency',
                            'occurrence_count', 'first_seen', 'last_seen']
