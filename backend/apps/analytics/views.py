"""Analytics app — Dashboard summary and spending analytics views."""

from decimal import Decimal
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.transactions.models import Transaction


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    GET /api/v1/summary/
    Returns today's spending, month-to-date, year-to-date, and wallet balance.
    This is what powers the Dashboard screen.
    """
    user = request.user
    now = timezone.now()
    today = now.date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    base_qs = Transaction.objects.filter(user=user, is_deleted=False)

    # Today
    today_spent = base_qs.filter(
        type='expense', transaction_date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    today_count = base_qs.filter(
        type='expense', transaction_date=today
    ).count()

    # This month
    month_expenses = base_qs.filter(
        type='expense', transaction_date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    month_income = base_qs.filter(
        type='income', transaction_date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # This year
    year_expenses = base_qs.filter(
        type='expense', transaction_date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    year_income = base_qs.filter(
        type='income', transaction_date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Wallet balance (all-time income - all-time expenses)
    total_income = base_qs.filter(
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_expenses = base_qs.filter(
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    wallet_balance = total_income - total_expenses

    # Savings jar (first active goal)
    from apps.budgets.models import SavingsGoal
    active_goal = SavingsGoal.objects.filter(
        user=user, status='active'
    ).first()

    savings_data = None
    if active_goal:
        savings_data = {
            'id': str(active_goal.id),
            'name': active_goal.name,
            'current': float(active_goal.current_amount),
            'target': float(active_goal.target_amount),
            'fill_state': active_goal.fill_state,
            'fill_percentage': active_goal.fill_percentage,
        }

    return Response({
        'today': {
            'total_spent': float(today_spent),
            'transaction_count': today_count,
        },
        'this_month': {
            'total_spent': float(month_expenses),
            'total_income': float(month_income),
            'net': float(month_income - month_expenses),
        },
        'this_year': {
            'total_spent': float(year_expenses),
            'total_income': float(year_income),
        },
        'wallet_balance': float(wallet_balance),
        'savings_jar': savings_data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_split(request):
    """
    GET /api/v1/analytics/category-split/
    Pie chart data: spending per category for current month.
    """
    now = timezone.now()
    month_start = now.date().replace(day=1)

    data = Transaction.objects.filter(
        user=request.user,
        type='expense',
        is_deleted=False,
        transaction_date__gte=month_start,
    ).values(
        'category__name', 'category__icon', 'category__color_hex'
    ).annotate(
        total=Sum('amount'),
        count=Count('id'),
    ).order_by('-total')

    results = []
    for item in data:
        results.append({
            'category': item['category__name'] or 'Uncategorized',
            'icon': item['category__icon'] or 'misc.png',
            'color': item['category__color_hex'] or '#6C5CE7',
            'total': float(item['total']),
            'count': item['count'],
        })

    return Response(results)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_trend(request):
    """
    GET /api/v1/analytics/weekly/
    Daily spending for the last 7 days, broken down by category.
    Powers the Analytics screen line charts.
    """
    now = timezone.now()
    week_start = (now - timezone.timedelta(days=6)).date()

    data = Transaction.objects.filter(
        user=request.user,
        type='expense',
        is_deleted=False,
        transaction_date__gte=week_start,
    ).values(
        'transaction_date', 'category__name'
    ).annotate(
        total=Sum('amount'),
    ).order_by('transaction_date')

    # Group by date
    from collections import defaultdict
    by_date = defaultdict(lambda: {'date': None, 'categories': {}, 'total': 0})

    for item in data:
        date_str = str(item['transaction_date'])
        cat = item['category__name'] or 'Uncategorized'
        amount = float(item['total'])

        by_date[date_str]['date'] = date_str
        by_date[date_str]['categories'][cat] = amount
        by_date[date_str]['total'] += amount

    return Response(list(by_date.values()))
