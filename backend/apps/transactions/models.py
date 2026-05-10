"""
PocketSense — Transaction & Category Models
Core financial data — every expense and income entry lives here.
"""

import uuid
from django.db import models
from django.conf import settings


class Category(models.Model):
    """
    Expense/income categories. System defaults + user-custom categories.
    System defaults have user=NULL.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='categories', null=True, blank=True,
        help_text="NULL = system default category"
    )
    name = models.CharField(max_length=50)
    icon = models.CharField(
        max_length=50, default='misc.png',
        help_text="Icon filename from assets/icons/"
    )
    color_hex = models.CharField(max_length=7, default='#6C5CE7')
    is_default = models.BooleanField(
        default=False,
        help_text="System-provided category that can't be deleted"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']
        # A user can't have two categories with the same name
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_category_per_user'
            )
        ]

    def __str__(self):
        owner = self.user.username if self.user else "SYSTEM"
        return f"{self.name} ({owner})"


class Transaction(models.Model):
    """
    Every expense and income entry.
    This is the most queried table — indexes are critical.
    """

    class TransactionType(models.TextChoices):
        EXPENSE = 'expense', 'Expense'
        INCOME = 'income', 'Income'

    class AutoCategory(models.TextChoices):
        MINOR = 'minor', 'Minor Expense'
        MAJOR = 'major', 'Major Expense'
        MINOR_REPETITIVE = 'minor_repetitive', 'Minor Repetitive'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='transactions'
    )

    type = models.CharField(max_length=10, choices=TransactionType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Always positive. Type field determines expense vs income."
    )
    transaction_date = models.DateField()

    # ML classification results
    auto_category = models.CharField(
        max_length=20, choices=AutoCategory.choices,
        blank=True, null=True,
        help_text="ML-assigned magnitude classification"
    )
    category_confidence = models.FloatField(
        null=True, blank=True,
        help_text="ML model confidence (0.0 to 1.0)"
    )

    # Sync tracking
    is_synced = models.BooleanField(
        default=True,
        help_text="False if created offline and not yet confirmed by server"
    )
    device_id = models.CharField(max_length=100, blank=True, default='')

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-transaction_date'], name='idx_txn_user_date'),
            models.Index(fields=['user', 'category'], name='idx_txn_user_category'),
            models.Index(fields=['user', 'type'], name='idx_txn_user_type'),
        ]

    def __str__(self):
        return f"{self.type}: {self.title} — ₹{self.amount}"


class IncomeSource(models.Model):
    """
    Registered sources of income (pocket money, salary, etc.)
    Used by the advice engine to understand financial constraints.
    """

    class Frequency(models.TextChoices):
        ONE_TIME = 'one_time', 'One Time'
        WEEKLY = 'weekly', 'Weekly'
        BI_MONTHLY = 'bi_monthly', 'Bi-Monthly'
        MONTHLY = 'monthly', 'Monthly'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='income_sources'
    )
    name = models.CharField(max_length=100, help_text="e.g. 'Parents', 'Part-time job'")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=Frequency.choices)
    next_expected = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'income_sources'

    def __str__(self):
        return f"{self.name}: ₹{self.amount}/{self.frequency}"


class RecurringPattern(models.Model):
    """
    Detected recurring expenses (e.g. ₹50 metro daily).
    Populated by the pattern detection engine, not by users directly.
    """

    class Frequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recurring_patterns'
    )
    pattern_title = models.CharField(max_length=200)
    avg_amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    occurrence_count = models.IntegerField(default=0)
    first_seen = models.DateField()
    last_seen = models.DateField()
    user_acknowledged = models.BooleanField(
        default=False,
        help_text="User has seen and confirmed this pattern"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recurring_patterns'

    def __str__(self):
        return f"Pattern: {self.pattern_title} (~₹{self.avg_amount}/{self.frequency})"
