"""Advice app — Context-aware financial advice API endpoint."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from .engine import get_advice


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_advice_view(request):
    """
    GET /api/v1/advice/
    Returns context-aware financial advice based on user profile and spending.
    """
    advice_list = get_advice(request.user)

    # Include profile context for frontend display
    profile_context = {}
    try:
        profile = request.user.profile
        profile_context = {
            'user_type': profile.age_group,
            'income_type': profile.income_type,
            'living_situation': profile.living_situation,
            'food_provided': profile.food_provided,
        }
    except UserProfile.DoesNotExist:
        pass

    return Response({
        'advice': advice_list,
        'profile_context': profile_context,
    })
