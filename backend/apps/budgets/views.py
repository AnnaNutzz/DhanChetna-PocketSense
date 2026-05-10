"""Budgets app — Views for Budget and SavingsGoal management."""

from decimal import Decimal
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Budget, SavingsGoal
from .serializers import BudgetSerializer, SavingsGoalSerializer, SavingsDepositSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    """CRUD for budgets (overall and per-category)."""
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(
            user=self.request.user
        ).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def status_check(self, request):
        """
        GET /api/v1/budgets/status_check/
        Returns current spending vs each active budget.
        """
        from django.db.models import Sum
        from django.utils import timezone
        from apps.transactions.models import Transaction

        now = timezone.now()
        budgets = Budget.objects.filter(
            user=request.user, is_active=True
        ).select_related('category')

        results = []
        for budget in budgets:
            # Calculate spending for the budget period
            if budget.period == 'monthly':
                start_date = now.replace(day=1).date()
            else:  # weekly
                start_date = (now - timezone.timedelta(days=now.weekday())).date()

            txn_filter = {
                'user': request.user,
                'type': 'expense',
                'is_deleted': False,
                'transaction_date__gte': start_date,
            }
            if budget.category:
                txn_filter['category'] = budget.category

            spent = Transaction.objects.filter(
                **txn_filter
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            percentage = min(100, round(float(spent) / float(budget.limit_amount) * 100))

            results.append({
                'budget_id': str(budget.id),
                'category': budget.category.name if budget.category else 'Overall',
                'limit': float(budget.limit_amount),
                'spent': float(spent),
                'remaining': float(budget.limit_amount - spent),
                'percentage': percentage,
                'status': 'over' if percentage >= 100 else 'warning' if percentage >= 80 else 'ok',
            })

        return Response(results)


class SavingsGoalViewSet(viewsets.ModelViewSet):
    """CRUD for savings jar goals."""
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['put'])
    def deposit(self, request, pk=None):
        """
        PUT /api/v1/savings/{id}/deposit/
        Add money to the savings jar.
        """
        goal = self.get_object()
        serializer = SavingsDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        goal.current_amount += amount

        # Auto-complete if target reached
        if goal.current_amount >= goal.target_amount:
            goal.status = 'completed'

        goal.save()

        return Response(SavingsGoalSerializer(goal).data)
