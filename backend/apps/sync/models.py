"""
PocketSense — Sync & Audit Models
Device sync tracking and audit log for financial data integrity.
"""

import uuid
from django.db import models
from django.conf import settings


class DeviceSync(models.Model):
    """
    Tracks sync state per device per user.
    Used by offline-first mode to resolve what needs pushing/pulling.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='devices'
    )
    device_id = models.CharField(max_length=100)
    device_name = models.CharField(max_length=200, blank=True, default='')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    pending_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device_syncs'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'device_id'],
                name='unique_device_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.username} — {self.device_name or self.device_id}"


class AuditLog(models.Model):
    """
    Immutable audit trail for all financial data changes.
    Non-negotiable for apps handling money.
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    action = models.CharField(
        max_length=20,
        help_text="created, updated, deleted"
    )
    entity_type = models.CharField(
        max_length=50,
        help_text="Model name: transaction, budget, savings_goal, etc."
    )
    entity_id = models.UUIDField(help_text="PK of the affected record")
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['user', '-created_at'],
                name='idx_audit_user_time'
            ),
        ]

    def __str__(self):
        return f"[{self.action}] {self.entity_type}:{self.entity_id}"
