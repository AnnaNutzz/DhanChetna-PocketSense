"""
Management command to create a demo user with sample data.
Run: python manage.py seed_demo_user

Updated to use 11 categories from DhanChetna paper with realistic
student spending patterns across hostel, food, transport, etc.
"""

from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.accounts.models import UserProfile
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

        # 2. Set up profile (hostel student — matches paper context)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.age_group = 'student'
        profile.income_type = 'pocket_money'
        profile.income_frequency = 'monthly'
        profile.income_amount = Decimal('8200')  # Paper's hostel mean
        profile.living_situation = 'hostel'
        profile.food_provided = True
        profile.onboarding_complete = True
        profile.save()
        self.stdout.write("  ✓ Set profile: hostel student, ₹8,200/month")

        # 3. Grab system categories
        cats = {c.name: c for c in Category.objects.filter(is_default=True)}

        # 4. Seed sample transactions (last 30 days, realistic student data)
        today = date.today()
        sample_txns = [
            # Food (dominant for hostel students — 38% per paper)
            ("Canteen Lunch", 80, "expense", "Food", 0),
            ("Zomato Order", 250, "expense", "Food", 0),
            ("Pocket Money", 8200, "income", "Income", 1),
            ("Maggi & Snacks", 60, "expense", "Food", 1),
            ("Canteen Lunch", 80, "expense", "Food", 2),
            ("Tea & Biscuits", 40, "expense", "Food", 2),
            ("Uber Auto", 150, "expense", "Transport", 3),
            ("Canteen Lunch", 80, "expense", "Food", 3),
            ("Swiggy Dinner", 320, "expense", "Food", 4),
            ("Bus Pass Recharge", 500, "expense", "Transport", 4),
            ("Notebook & Pens", 180, "expense", "Stationery", 5),
            ("Canteen Lunch", 80, "expense", "Food", 5),
            ("Movie Tickets", 350, "expense", "Entertainment", 6),
            ("Netflix", 199, "expense", "Subscriptions", 6),
            ("Metro Card", 200, "expense", "Transport", 7),
            ("Canteen Lunch", 80, "expense", "Food", 7),
            ("T-shirt Myntra", 599, "expense", "Clothing", 8),
            ("Cold Drink", 40, "expense", "Food", 8),
            ("Mobile Recharge", 299, "expense", "Communication", 9),
            ("Canteen Lunch", 80, "expense", "Food", 9),
            ("Medicines", 250, "expense", "Medical", 10),
            ("Print Outs", 50, "expense", "Stationery", 10),
            ("Electricity Split", 400, "expense", "Utilities", 11),
            ("Freelance Work", 3000, "income", "Income", 11),
            ("Canteen Lunch", 80, "expense", "Food", 12),
            ("Auto Fare", 120, "expense", "Transport", 12),
            ("Face Wash", 180, "expense", "Personal Care", 13),
            ("Canteen Lunch", 80, "expense", "Food", 13),
            ("Amazon Book", 450, "expense", "Miscellaneous", 14),
            ("Tea & Biscuits", 40, "expense", "Food", 14),
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

        # 5. Seed budgets
        Budget.objects.create(
            user=user,
            category=cats.get("Food"),
            limit_amount=Decimal("3500"),
            period="monthly",
        )
        Budget.objects.create(
            user=user,
            category=cats.get("Transport"),
            limit_amount=Decimal("1500"),
            period="monthly",
        )
        Budget.objects.create(
            user=user,
            category=cats.get("Entertainment"),
            limit_amount=Decimal("1000"),
            period="monthly",
        )
        self.stdout.write("  ✓ Created 3 sample budgets")

        # 6. Seed savings goals
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
