from django.contrib import admin
from .models import DeviceSync, AuditLog


@admin.register(DeviceSync)
class DeviceSyncAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_id', 'device_name', 'last_sync_at', 'pending_count']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'entity_type', 'entity_id', 'created_at']
    list_filter = ['action', 'entity_type']
    date_hierarchy = 'created_at'
    readonly_fields = ['user', 'action', 'entity_type', 'entity_id',
                       'old_values', 'new_values', 'ip_address', 'created_at']
