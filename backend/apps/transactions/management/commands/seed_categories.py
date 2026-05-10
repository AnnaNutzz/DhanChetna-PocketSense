"""
Management command to seed default categories.
Run: python manage.py seed_categories

Updated to match the 11 categories from the DhanChetna paper:
Food, Transport, Stationery, Entertainment, Clothing, Utilities,
Subscriptions, Medical, Communication, Personal Care, Miscellaneous
"""

from django.core.management.base import BaseCommand
from apps.transactions.models import Category


# 11 categories matching the DhanChetna paper (Table IV)
DEFAULT_CATEGORIES = [
    {'name': 'Food', 'icon': 'food.png', 'color_hex': '#FF6B6B'},
    {'name': 'Transport', 'icon': 'travel.png', 'color_hex': '#4ECDC4'},
    {'name': 'Stationery', 'icon': 'misc.png', 'color_hex': '#A29BFE'},
    {'name': 'Entertainment', 'icon': 'misc.png', 'color_hex': '#FD79A8'},
    {'name': 'Clothing', 'icon': 'cart.png', 'color_hex': '#45B7D1'},
    {'name': 'Utilities', 'icon': 'recurring.png', 'color_hex': '#F39C12'},
    {'name': 'Subscriptions', 'icon': 'subscription.png', 'color_hex': '#96CEB4'},
    {'name': 'Medical', 'icon': 'misc.png', 'color_hex': '#E17055'},
    {'name': 'Communication', 'icon': 'misc.png', 'color_hex': '#00B894'},
    {'name': 'Personal Care', 'icon': 'misc.png', 'color_hex': '#FDCB6E'},
    {'name': 'Miscellaneous', 'icon': 'misc.png', 'color_hex': '#6C5CE7'},
    # Keep legacy categories for backward compat
    {'name': 'Shopping', 'icon': 'cart.png', 'color_hex': '#45B7D1'},
    {'name': 'Income', 'icon': 'income.png', 'color_hex': '#2ECC71'},
    {'name': 'Recurring', 'icon': 'recurring.png', 'color_hex': '#F39C12'},
]


class Command(BaseCommand):
    help = 'Seed default expense/income categories (11 from DhanChetna paper + legacy)'

    def handle(self, *args, **options):
        created_count = 0
        for cat_data in DEFAULT_CATEGORIES:
            _, created = Category.objects.get_or_create(
                name=cat_data['name'],
                user=None,  # System default
                defaults={
                    'icon': cat_data['icon'],
                    'color_hex': cat_data['color_hex'],
                    'is_default': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Created: {cat_data['name']}")
            else:
                self.stdout.write(f"  - Exists: {cat_data['name']}")

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {created_count} new categories.'
        ))
