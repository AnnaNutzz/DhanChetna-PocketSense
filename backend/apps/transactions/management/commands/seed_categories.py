"""
Management command to seed default categories.
Run: python manage.py seed_categories
"""

from django.core.management.base import BaseCommand
from apps.transactions.models import Category


# Default categories matching the existing icon assets
DEFAULT_CATEGORIES = [
    {'name': 'Food', 'icon': 'food.png', 'color_hex': '#FF6B6B'},
    {'name': 'Travel', 'icon': 'travel.png', 'color_hex': '#4ECDC4'},
    {'name': 'Shopping', 'icon': 'cart.png', 'color_hex': '#45B7D1'},
    {'name': 'Subscriptions', 'icon': 'subscription.png', 'color_hex': '#96CEB4'},
    {'name': 'Income', 'icon': 'income.png', 'color_hex': '#2ECC71'},
    {'name': 'Recurring', 'icon': 'recurring.png', 'color_hex': '#F39C12'},
    {'name': 'Miscellaneous', 'icon': 'misc.png', 'color_hex': '#6C5CE7'},
]


class Command(BaseCommand):
    help = 'Seed default expense/income categories'

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
