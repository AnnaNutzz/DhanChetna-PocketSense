"""
PocketSense — Recurring Expense Detection Engine
Rule-based frequency analysis (selected in the paper over DBSCAN/LSTM/IsolationForest).

Paper specs:
- Groups transactions by category
- Compares pairs using token sort ratio (fuzzywuzzy, threshold >= 80%)
- Checks for monthly regularity (28-33 day intervals) within ±10% amount tolerance
- Achieved 88.4% precision and 91.2% recall
"""

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg
from django.utils import timezone

from apps.transactions.models import Transaction, RecurringPattern

try:
    from fuzzywuzzy import fuzz
except ImportError:
    fuzz = None


def _fuzzy_match(title1, title2, threshold=80):
    """Compare two titles using token sort ratio. Falls back to exact match if fuzzywuzzy unavailable."""
    if fuzz is not None:
        return fuzz.token_sort_ratio(title1.lower(), title2.lower()) >= threshold
    return title1.lower().strip() == title2.lower().strip()


def _is_regular_interval(dates, min_interval=28, max_interval=33):
    """Check if dates show monthly regularity (28-33 day intervals)."""
    if len(dates) < 2:
        return False
    sorted_dates = sorted(dates)
    intervals = [(sorted_dates[i+1] - sorted_dates[i]).days for i in range(len(sorted_dates)-1)]
    if not intervals:
        return False
    regular_count = sum(1 for iv in intervals if min_interval <= iv <= max_interval)
    return regular_count >= len(intervals) * 0.5  # At least half must be regular


def _within_amount_tolerance(amounts, tolerance=0.10):
    """Check if amounts are within ±10% of each other."""
    if len(amounts) < 2:
        return False
    avg = sum(amounts) / len(amounts)
    if avg == 0:
        return True
    return all(abs(a - avg) / avg <= tolerance for a in amounts)


def detect_patterns(user, lookback_days=120):
    """
    Detect recurring expense patterns for a user.
    Groups by category, then fuzzy-matches titles within each category.
    Returns list of detected pattern dicts.
    """
    cutoff = timezone.now().date() - timedelta(days=lookback_days)
    expenses = Transaction.objects.filter(
        user=user,
        type='expense',
        is_deleted=False,
        transaction_date__gte=cutoff,
    ).order_by('transaction_date')

    if not expenses.exists():
        return []

    # Group by category
    by_category = defaultdict(list)
    for txn in expenses:
        cat_name = txn.category.name if txn.category else 'Uncategorized'
        by_category[cat_name].append(txn)

    detected = []

    for cat_name, txns in by_category.items():
        # Cluster similar titles within each category
        clusters = []
        used = set()

        for i, txn_a in enumerate(txns):
            if i in used:
                continue
            cluster = [txn_a]
            used.add(i)

            for j, txn_b in enumerate(txns):
                if j in used:
                    continue
                if _fuzzy_match(txn_a.title, txn_b.title):
                    cluster.append(txn_b)
                    used.add(j)

            if len(cluster) >= 3:
                clusters.append(cluster)

        # Check each cluster for regularity
        for cluster in clusters:
            dates = [t.transaction_date for t in cluster]
            amounts = [float(t.amount) for t in cluster]

            is_monthly = _is_regular_interval(dates)
            is_weekly = _is_regular_interval(dates, min_interval=5, max_interval=9)
            amount_consistent = _within_amount_tolerance(amounts)

            if (is_monthly or is_weekly) and amount_consistent:
                freq = 'monthly' if is_monthly else 'weekly'
            elif len(cluster) >= 5:
                # High frequency even without strict regularity
                freq = 'daily'
            else:
                continue

            avg_amount = sum(amounts) / len(amounts)
            pattern_title = cluster[0].title

            detected.append({
                'pattern_title': pattern_title,
                'avg_amount': round(avg_amount, 2),
                'frequency': freq,
                'occurrence_count': len(cluster),
                'first_seen': min(dates),
                'last_seen': max(dates),
                'category': cat_name,
            })

    return detected


def update_recurring_patterns(user):
    """
    Run pattern detection and update the RecurringPattern model.
    Called periodically or on-demand from advice engine.
    """
    detected = detect_patterns(user)

    for pat in detected:
        obj, created = RecurringPattern.objects.update_or_create(
            user=user,
            pattern_title=pat['pattern_title'],
            defaults={
                'avg_amount': Decimal(str(pat['avg_amount'])),
                'frequency': pat['frequency'],
                'occurrence_count': pat['occurrence_count'],
                'first_seen': pat['first_seen'],
                'last_seen': pat['last_seen'],
            }
        )

    return detected
