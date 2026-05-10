"""
PocketSense — Rules-Based Expense Classifier (Phase 1)
Classifies transactions as minor/major/minor_repetitive.
Phase 2 will add ML (TF-IDF + Logistic Regression).
"""

from django.db.models import Count
from apps.accounts.models import UserProfile


def classify_expense(transaction):
    """
    Classify a transaction's magnitude. Returns (auto_category, confidence).
    Rules-based: uses amount/income ratio and frequency.
    """
    try:
        profile = transaction.user.profile
        income = float(profile.income_amount) if profile.income_amount else 0
    except UserProfile.DoesNotExist:
        income = 0

    amount = float(transaction.amount)

    if income <= 0:
        # No income data — use absolute thresholds (student defaults)
        if amount < 100:
            return ('minor', 0.6)
        elif amount < 1000:
            return ('minor', 0.5)
        else:
            return ('major', 0.5)

    ratio = amount / income

    # Check frequency of similar transactions (same title, last 30 days)
    from datetime import timedelta
    from django.utils import timezone
    from apps.transactions.models import Transaction

    recent_count = Transaction.objects.filter(
        user=transaction.user,
        title__iexact=transaction.title,
        is_deleted=False,
        transaction_date__gte=timezone.now().date() - timedelta(days=30),
    ).exclude(id=transaction.id).count()

    if recent_count >= 3 and ratio < 0.05:
        return ('minor_repetitive', 0.85)
    elif ratio < 0.10:
        return ('minor', 0.80)
    else:
        return ('major', 0.75)
