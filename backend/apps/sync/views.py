"""Sync app — Placeholder for Phase 2 offline sync."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_push(request):
    """
    POST /api/v1/sync/push/
    Upload offline transactions. Phase 2 implementation.
    """
    return Response({
        'synced': 0,
        'conflicts': [],
        'message': 'Sync engine coming in Phase 2!',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_pull(request):
    """
    GET /api/v1/sync/pull/
    Pull latest transactions from server. Phase 2 implementation.
    """
    return Response({
        'transactions': [],
        'message': 'Sync engine coming in Phase 2!',
    })
