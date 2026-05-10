"""
PocketSense — Context-Aware Advice Engine (Phase 1: Rules-Based)
Generates financial advice based on user profile + transaction history.

Paper rules implemented:
- Food spend > 45% of monthly income (hostel): suggest mess plan
- Entertainment spend > 20%: review active subscriptions
- Budget utilisation > 90% before 20th: defer non-essential purchases
- >= 3 recurring patterns: surface committed expense breakdown
"""

from decimal import Decimal
from collections import defaultdict
from datetime import timedelta
from django.db.models import Sum, Count
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.transactions.models import Transaction, RecurringPattern
from apps.budgets.models import Budget, SavingsGoal


def get_advice(user):
    """Generate context-aware advice for a user. Returns list of advice dicts."""
    advice_list = []

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        return [{'type': 'awareness', 'message': 'Complete your profile in Settings so we can give personalized advice.', 'confidence': 'high', 'data_points': 0}]

    now = timezone.now()
    today = now.date()
    month_start = today.replace(day=1)
    day_of_month = today.day
    income_amount = float(profile.income_amount) if profile.income_amount else 0

    base = Transaction.objects.filter(user=user, is_deleted=False)
    month_expenses = base.filter(type='expense', transaction_date__gte=month_start)

    # --- Category totals for the month ---
    cat_totals = month_expenses.values('category__name').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')

    total_spent = sum(float(c['total']) for c in cat_totals) if cat_totals else 0
    cat_map = {c['category__name'] or 'Uncategorized': float(c['total']) for c in cat_totals}
    total_data_points = sum(c['count'] for c in cat_totals) if cat_totals else 0

    # === PAPER RULE 1: Food > 45% for hostel students ===
    food_spent = cat_map.get('Food', 0)
    if total_spent > 0 and food_spent / total_spent > 0.45:
        pct = round(food_spent / total_spent * 100)
        if profile.living_situation == 'hostel' and profile.food_provided:
            advice_list.append({
                'type': 'awareness',
                'message': f"{pct}% of your spending is on Food. Since your hostel provides meals, this might be compensatory spending. Consider using the mess plan more and buying snacks in bulk weekly.",
                'confidence': 'high',
                'data_points': total_data_points,
            })
        elif profile.living_situation == 'hostel':
            advice_list.append({
                'type': 'optimization',
                'message': f"{pct}% of your spending is on Food. Consider subscribing to a hostel mess plan if available — it's usually cheaper than ordering every meal.",
                'confidence': 'high',
                'data_points': total_data_points,
            })
        else:
            advice_list.append({
                'type': 'awareness',
                'message': f"{pct}% of your spending is on Food. Meal planning or cooking batches could reduce this significantly.",
                'confidence': 'medium',
                'data_points': total_data_points,
            })

    # === PAPER RULE 2: Entertainment > 20% ===
    entertainment_spent = cat_map.get('Entertainment', 0)
    if total_spent > 0 and entertainment_spent / total_spent > 0.20:
        pct = round(entertainment_spent / total_spent * 100)
        advice_list.append({
            'type': 'optimization',
            'message': f"Entertainment is {pct}% of your spending this month. Review your active subscriptions — are you using all of them?",
            'confidence': 'medium',
            'data_points': total_data_points,
        })

    # === PAPER RULE 3: Budget > 90% before 20th ===
    budgets = Budget.objects.filter(user=user, is_active=True).select_related('category')
    for budget in budgets:
        if budget.period == 'monthly':
            start = month_start
        else:
            start = (now - timedelta(days=now.weekday())).date()

        filt = {'user': user, 'type': 'expense', 'is_deleted': False, 'transaction_date__gte': start}
        if budget.category:
            filt['category'] = budget.category

        spent = Transaction.objects.filter(**filt).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        pct = float(spent) / float(budget.limit_amount) * 100 if budget.limit_amount else 0
        cat_name = budget.category.name if budget.category else 'Overall'

        if pct >= 100:
            advice_list.append({
                'type': 'awareness',
                'message': f"⚠️ You've exceeded your {cat_name} budget (₹{float(spent):.0f}/₹{float(budget.limit_amount):.0f})! Consider pausing non-essential spending.",
                'confidence': 'high',
                'data_points': 1,
            })
        elif pct >= 90 and day_of_month < 20:
            advice_list.append({
                'type': 'prediction',
                'message': f"{cat_name} budget is at {pct:.0f}% and it's only the {day_of_month}th. Defer non-essential {cat_name.lower()} purchases to stay within budget.",
                'confidence': 'high',
                'data_points': 1,
            })
        elif pct >= 80:
            advice_list.append({
                'type': 'prediction',
                'message': f"{cat_name} budget is at {pct:.0f}%. ₹{float(budget.limit_amount - spent):.0f} remaining for the rest of the period.",
                'confidence': 'high',
                'data_points': 1,
            })

    # === PAPER RULE 4: >= 3 recurring patterns ===
    patterns = RecurringPattern.objects.filter(user=user)
    if patterns.count() >= 3:
        total_committed = sum(float(p.avg_amount) for p in patterns)
        advice_list.append({
            'type': 'awareness',
            'message': f"You have {patterns.count()} recurring expenses totalling ~₹{total_committed:.0f}/month. These committed costs take priority — plan your discretionary spending around them.",
            'confidence': 'high',
            'data_points': patterns.count(),
        })

    # === Repetitive small expenses (optimization) ===
    week_start = (now - timedelta(days=7)).date()
    recent = base.filter(type='expense', transaction_date__gte=week_start)
    title_groups = recent.values('title').annotate(
        count=Count('id'), total=Sum('amount')
    ).filter(count__gte=3).order_by('-count')

    for grp in title_groups[:2]:
        avg = float(grp['total']) / grp['count']
        monthly_est = avg * grp['count'] * 4
        advice_list.append({
            'type': 'optimization',
            'message': f'You buy "{grp["title"]}" {grp["count"]}x/week averaging ₹{avg:.0f} each (~₹{monthly_est:.0f}/month). Buying in bulk could save ~₹{monthly_est * 0.2:.0f}/month.',
            'confidence': 'medium',
            'data_points': grp['count'],
        })

    # === Burn rate prediction ===
    if income_amount > 0 and total_spent > 0:
        days_elapsed = max((today - month_start).days, 1)
        daily_rate = total_spent / days_elapsed
        projected = daily_rate * 30

        if projected > income_amount:
            days_until_broke = int(income_amount / daily_rate)
            exhaust_date = month_start + timedelta(days=days_until_broke)
            advice_list.append({
                'type': 'prediction',
                'message': f"At your current pace (₹{daily_rate:.0f}/day), you'll exhaust this month's income by {exhaust_date.strftime('%b %d')}.",
                'confidence': 'high',
                'data_points': days_elapsed,
            })

    # === Savings encouragement ===
    active_goals = SavingsGoal.objects.filter(user=user, status='active')
    for goal in active_goals:
        if goal.fill_percentage < 25:
            advice_list.append({
                'type': 'optimization',
                'message': f'Your "{goal.name}" goal is only {goal.fill_percentage}% funded. Try depositing small amounts weekly!',
                'confidence': 'medium',
                'data_points': 1,
            })

    if not advice_list:
        advice_list.append({
            'type': 'awareness',
            'message': 'Keep tracking your expenses! We need more data to give personalized advice.',
            'confidence': 'low',
            'data_points': 0,
        })

    return advice_list
