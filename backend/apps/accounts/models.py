"""
PocketSense — User & Profile Models
Custom User model with Firebase UID, and UserProfile for financial context.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Uses Firebase UID as the primary identity link.
    Django's built-in fields (username, email, password, etc.) are inherited.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firebase_uid = models.CharField(
        max_length=128, unique=True, blank=True, null=True,
        help_text="Firebase Authentication UID"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.email})"


class UserProfile(models.Model):
    """
    Financial context for the advice engine.
    This is what makes PocketSense smarter than generic trackers.
    """

    class AgeGroup(models.TextChoices):
        STUDENT = 'student', 'Student'
        WORKING = 'working', 'Working Adult'
        FREELANCER = 'freelancer', 'Freelancer'
        RETIRED = 'retired', 'Retired'

    class IncomeType(models.TextChoices):
        POCKET_MONEY = 'pocket_money', 'Pocket Money'
        SALARY = 'salary', 'Salary'
        STIPEND = 'stipend', 'Stipend'
        FREELANCE = 'freelance', 'Freelance Income'
        NONE = 'none', 'No Income'

    class IncomeFrequency(models.TextChoices):
        WEEKLY = 'weekly', 'Weekly'
        BI_MONTHLY = 'bi_monthly', 'Bi-Monthly'
        MONTHLY = 'monthly', 'Monthly'
        IRREGULAR = 'irregular', 'Irregular'

    class LivingSituation(models.TextChoices):
        HOSTEL = 'hostel', 'Hostel'
        HOME = 'home', 'Living at Home'
        RENTED = 'rented', 'Rented Place'
        PG = 'pg', 'Paying Guest'

    class ThemePreference(models.TextChoices):
        DARK = 'dark', 'Dark Mode'
        LIGHT = 'light', 'Light Mode'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )

    # Financial context
    age_group = models.CharField(
        max_length=20, choices=AgeGroup.choices, default=AgeGroup.STUDENT
    )
    income_type = models.CharField(
        max_length=20, choices=IncomeType.choices, default=IncomeType.POCKET_MONEY
    )
    income_frequency = models.CharField(
        max_length=20, choices=IncomeFrequency.choices, default=IncomeFrequency.MONTHLY
    )
    income_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Average income per period (in INR)"
    )
    living_situation = models.CharField(
        max_length=20, choices=LivingSituation.choices, default=LivingSituation.HOSTEL
    )
    food_provided = models.BooleanField(
        default=False,
        help_text="Does the living situation include meals?"
    )

    # Preferences
    currency = models.CharField(max_length=3, default='INR')
    theme_preference = models.CharField(
        max_length=10, choices=ThemePreference.choices, default=ThemePreference.DARK
    )

    # Onboarding
    onboarding_complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profile: {self.user.username} ({self.age_group})"
