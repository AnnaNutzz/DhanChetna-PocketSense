"""
PocketSense — Budget & Savings Models
Budget limits and savings jar goals.
"""

import uuid
from django.db import models
from django.conf import settings


class Budget(models.Model):
    """
    Spending limits — either overall or per-category.
    category=NULL means overall monthly budget.
    """

    class Period(models.TextChoices):
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.ForeignKey(
        'transactions.Category', on_delete=models.CASCADE,
        null=True, blank=True,
        help_text="NULL = overall budget (all categories)"
    )
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(
        max_length=10, choices=Period.choices, default=Period.MONTHLY
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budgets'

    def __str__(self):
        target = self.category.name if self.category else "Overall"
        return f"Budget: {target} — ₹{self.limit_amount}/{self.period}"


class SavingsGoal(models.Model):
    """
    Savings jar — users set a target and watch the jar fill up.
    Maps to the 4-state jar sprites: no-savings, less, more, full.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        ABANDONED = 'abandoned', 'Abandoned'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='savings_goals'
    )
    name = models.CharField(max_length=100, default='My Savings Jar')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'savings_goals'

    @property
    def fill_state(self):
        """Maps to jar sprite: no-savings, less-savings, more-savings, full-savings"""
        if self.target_amount == 0:
            return 'no-savings'
        ratio = float(self.current_amount) / float(self.target_amount)
        if ratio <= 0:
            return 'no-savings'
        elif ratio < 0.4:
            return 'less-savings'
        elif ratio < 0.8:
            return 'more-savings'
        else:
            return 'full-savings'

    @property
    def fill_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(100, round(float(self.current_amount) / float(self.target_amount) * 100))

    def __str__(self):
        return f"{self.name}: ₹{self.current_amount}/₹{self.target_amount}"
