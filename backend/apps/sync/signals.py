"""
PocketSense — Audit Logging Signals
Auto-logs create/update/delete for financial models (Transaction, Budget, SavingsGoal).
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.transactions.models import Transaction
from apps.budgets.models import Budget, SavingsGoal
from .models import AuditLog


def _log(user, action, entity_type, entity_id, old_values=None, new_values=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
    )


@receiver(post_save, sender=Transaction)
def log_transaction(sender, instance, created, **kwargs):
    _log(
        user=instance.user,
        action='created' if created else 'updated',
        entity_type='transaction',
        entity_id=instance.id,
        new_values={
            'title': instance.title,
            'type': instance.type,
            'amount': str(instance.amount),
            'category': str(instance.category_id) if instance.category_id else None,
        },
    )


@receiver(post_save, sender=Budget)
def log_budget(sender, instance, created, **kwargs):
    _log(
        user=instance.user,
        action='created' if created else 'updated',
        entity_type='budget',
        entity_id=instance.id,
        new_values={
            'limit_amount': str(instance.limit_amount),
            'category': str(instance.category_id) if instance.category_id else 'Overall',
            'period': instance.period,
        },
    )


@receiver(post_save, sender=SavingsGoal)
def log_savings(sender, instance, created, **kwargs):
    _log(
        user=instance.user,
        action='created' if created else 'updated',
        entity_type='savings_goal',
        entity_id=instance.id,
        new_values={
            'name': instance.name,
            'current_amount': str(instance.current_amount),
            'target_amount': str(instance.target_amount),
            'status': instance.status,
        },
    )
