"""Sync app — Offline sync push/pull endpoints."""

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from .models import DeviceSync


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_push(request):
    """
    POST /api/v1/sync/push/
    Upload offline transactions from a device.
    """
    device_id = request.data.get('device_id', '')
    transactions = request.data.get('transactions', [])
    last_sync = request.data.get('last_sync_at')

    synced = 0
    server_id_map = {}
    conflicts = []

    for txn_data in transactions:
        local_id = txn_data.get('local_id', '')
        try:
            obj = Transaction.objects.create(
                user=request.user,
                type=txn_data.get('type', 'expense'),
                title=txn_data.get('title', ''),
                amount=txn_data.get('amount', 0),
                transaction_date=txn_data.get('transaction_date', timezone.now().date()),
                description=txn_data.get('description', ''),
                device_id=device_id,
                is_synced=True,
            )
            server_id_map[local_id] = str(obj.id)
            synced += 1
        except Exception as e:
            conflicts.append({'local_id': local_id, 'error': str(e)})

    # Update device sync record
    if device_id:
        ds, _ = DeviceSync.objects.get_or_create(
            user=request.user,
            device_id=device_id,
            defaults={'device_name': request.data.get('device_name', '')}
        )
        ds.last_sync_at = timezone.now()
        ds.pending_count = 0
        ds.save()

    return Response({
        'synced': synced,
        'conflicts': conflicts,
        'server_id_map': server_id_map,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_pull(request):
    """
    GET /api/v1/sync/pull/?since=2026-02-16T10:00:00Z
    Pull transactions updated after a given timestamp.
    """
    since = request.query_params.get('since')
    qs = Transaction.objects.filter(user=request.user, is_deleted=False)

    if since:
        qs = qs.filter(updated_at__gt=since)

    qs = qs.order_by('-updated_at')[:200]
    serializer = TransactionSerializer(qs, many=True)

    return Response({
        'transactions': serializer.data,
        'server_time': timezone.now().isoformat(),
    })
