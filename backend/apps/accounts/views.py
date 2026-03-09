"""Accounts app — Views for auth verification and profile management."""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User, UserProfile
from .serializers import UserSerializer, UserProfileSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    """
    POST /api/v1/auth/verify/
    Verify Firebase token and return user data.
    In development without Firebase, creates a dev user.
    """
    firebase_token = request.data.get('firebase_token')

    if not firebase_token:
        return Response(
            {'error': 'firebase_token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # If Firebase auth is working, the middleware already verified the token.
    # This endpoint exists so the frontend can explicitly verify + get user data.

    # For development: create a test user if no Firebase
    from apps.accounts.authentication import _get_firebase_auth
    firebase_auth = _get_firebase_auth()

    if firebase_auth is None:
        # Dev mode: create/get a dummy user
        user, created = User.objects.get_or_create(
            username='dev_user',
            defaults={'email': 'dev@pocketsense.local'}
        )
        if created:
            UserProfile.objects.create(user=user)
    else:
        try:
            decoded = firebase_auth.verify_id_token(firebase_token)
            firebase_uid = decoded['uid']
            user = User.objects.get(firebase_uid=firebase_uid)
            created = False
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found. Token may be for an unregistered account.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Token verification failed: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    serializer = UserSerializer(user)
    return Response({
        'user': serializer.data,
        'is_new_user': not user.profile.onboarding_complete,
    })


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/v1/auth/profile/  — Get current user's profile
    PUT /api/v1/auth/profile/  — Update profile (onboarding)
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
