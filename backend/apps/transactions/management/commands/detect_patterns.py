"""
Management command to detect recurring expense patterns for all users.
Run: python manage.py detect_patterns
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.transactions.pattern_detector import update_recurring_patterns

User = get_user_model()


class Command(BaseCommand):
    help = 'Run recurring expense detection for all users (or a specific user)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Run for a specific user only')

    def handle(self, *args, **options):
        username = options.get('username')

        if username:
            users = User.objects.filter(username=username)
        else:
            users = User.objects.filter(is_active=True)

        for user in users:
            patterns = update_recurring_patterns(user)
            self.stdout.write(f"  {user.username}: {len(patterns)} patterns detected")

        self.stdout.write(self.style.SUCCESS('Done!'))
