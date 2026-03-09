"""Advice app — Placeholder for Phase 2 advice engine."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_advice(request):
    """
    GET /api/v1/advice/
    Returns context-aware financial advice.
    Phase 1: returns placeholder. Phase 2: rules engine. Phase 3: ML.
    """
    return Response({
        'advice': [],
        'message': 'Advice engine coming in Phase 2! Keep tracking your expenses.',
    })
