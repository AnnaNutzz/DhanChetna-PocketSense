"""Transactions app — Views for Transaction, Category, IncomeSource CRUD."""

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Category, Transaction, IncomeSource, RecurringPattern
from .serializers import (
    CategorySerializer, TransactionSerializer, TransactionCreateSerializer,
    IncomeSourceSerializer, RecurringPatternSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for expense/income categories.
    Returns system defaults + user's custom categories.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show system defaults (user=NULL) + user's own categories
        from django.db.models import Q
        return Category.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD for expenses and income.
    Soft-deletes only (is_deleted flag) — never hard delete financial data.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['type', 'category', 'transaction_date']
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    ordering = ['-transaction_date', '-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TransactionCreateSerializer
        return TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            is_deleted=False,
        ).select_related('category')

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        # TODO: Trigger ML categorization here (Phase 2)
        # TODO: Check budget limits and return warning (Phase 1)

    def perform_destroy(self, instance):
        """Soft delete — never hard delete financial data."""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class IncomeSourceViewSet(viewsets.ModelViewSet):
    """CRUD for registered income sources."""
    serializer_class = IncomeSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecurringPatternViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only — patterns are detected by the engine, not created by users.
    Users can only acknowledge them.
    """
    serializer_class = RecurringPatternSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecurringPattern.objects.filter(user=self.request.user)
