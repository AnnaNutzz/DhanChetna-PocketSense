"""
Management command to create a demo user with sample data.
Run: python manage.py seed_demo_user
"""

from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.transactions.models import Transaction, Category
from apps.budgets.models import Budget, SavingsGoal


DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo1234"
DEMO_EMAIL = "demo@pocketsense.app"

User = get_user_model()


class Command(BaseCommand):
    help = "Create a demo user with sample transactions, budgets, and savings goals"

    def handle(self, *args, **options):
        # 1. Create or reset the demo user
        user, created = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={
                "email": DEMO_EMAIL,
                "first_name": "Demo",
            },
        )
        user.set_password(DEMO_PASSWORD)
        user.save()

        if created:
            self.stdout.write(f"  ✓ Created user: {DEMO_USERNAME}")
        else:
            self.stdout.write(f"  - User exists: {DEMO_USERNAME}")
            # Clear old demo data so we get a fresh set
            Transaction.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()
            SavingsGoal.objects.filter(user=user).delete()
            self.stdout.write("  ✓ Cleared old demo data")

        # 2. Grab system categories
        cats = {c.name: c for c in Category.objects.filter(is_default=True)}

        # 3. Seed sample transactions (last 14 days)
        today = date.today()
        sample_txns = [
            ("Grocery Run", 850, "expense", "Food", 0),
            ("Freelance Payment", 15000, "income", "Income", 0),
            ("Netflix", 649, "expense", "Subscriptions", 1),
            ("Uber Ride", 320, "expense", "Travel", 1),
            ("Coffee & Snacks", 180, "expense", "Food", 2),
            ("Amazon Order", 2499, "expense", "Shopping", 2),
            ("Salary", 45000, "income", "Income", 3),
            ("Electricity Bill", 1200, "expense", "Recurring", 3),
            ("Lunch Out", 450, "expense", "Food", 4),
            ("Train Ticket", 780, "expense", "Travel", 5),
            ("Birthday Gift", 1500, "expense", "Shopping", 5),
            ("YouTube Premium", 129, "expense", "Subscriptions", 6),
            ("Dinner Party", 2200, "expense", "Food", 7),
            ("Side Project", 8000, "income", "Income", 8),
            ("Medicines", 350, "expense", "Miscellaneous", 9),
            ("Groceries", 1100, "expense", "Food", 10),
            ("Bus Pass", 500, "expense", "Travel", 11),
            ("Online Course", 999, "expense", "Miscellaneous", 12),
            ("Snacks", 220, "expense", "Food", 13),
            ("Interest Income", 1200, "income", "Income", 13),
        ]

        for title, amount, txn_type, cat_name, days_ago in sample_txns:
            Transaction.objects.create(
                user=user,
                title=title,
                amount=Decimal(str(amount)),
                type=txn_type,
                category=cats.get(cat_name),
                transaction_date=today - timedelta(days=days_ago),
            )
        self.stdout.write(f"  ✓ Created {len(sample_txns)} sample transactions")

        # 4. Seed budgets
        Budget.objects.create(
            user=user,
            category=cats.get("Food"),
            limit_amount=Decimal("5000"),
            period="monthly",
        )
        Budget.objects.create(
            user=user,
            category=cats.get("Shopping"),
            limit_amount=Decimal("3000"),
            period="monthly",
        )
        self.stdout.write("  ✓ Created 2 sample budgets")

        # 5. Seed savings goals
        SavingsGoal.objects.create(
            user=user,
            name="Emergency Fund",
            target_amount=Decimal("50000"),
            current_amount=Decimal("18500"),
            status="active",
        )
        SavingsGoal.objects.create(
            user=user,
            name="New Laptop",
            target_amount=Decimal("80000"),
            current_amount=Decimal("80000"),
            status="completed",
        )
        self.stdout.write("  ✓ Created 2 savings goals")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Demo account ready.\n"
            f"  Username: {DEMO_USERNAME}\n"
            f"  Password: {DEMO_PASSWORD}"
        ))
