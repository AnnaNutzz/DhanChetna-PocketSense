"""
PocketSense — Firebase Authentication Backend for DRF
Verifies Firebase ID tokens and maps them to Django User objects.
"""

import logging
from rest_framework import authentication, exceptions
from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy-initialize Firebase to avoid import-time errors if credentials are missing
_firebase_app = None


def _get_firebase_auth():
    """Initialize Firebase Admin SDK on first use."""
    global _firebase_app
    if _firebase_app is None:
        try:
            import firebase_admin
            from firebase_admin import credentials
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            _firebase_app = firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.warning(f"Firebase init failed: {e}. Auth will be unavailable.")
            return None
    from firebase_admin import auth
    return auth


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class that validates Firebase ID tokens.

    Usage: Client sends header:
        Authorization: Bearer <firebase_id_token>

    The backend verifies the token, extracts the Firebase UID,
    and returns the corresponding Django User (creating one if needed).
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None  # No Firebase token → let other auth classes try

        token = auth_header.split('Bearer ')[1].strip()

        if not token:
            return None

        firebase_auth = _get_firebase_auth()
        if firebase_auth is None:
            # Firebase not configured — in development, fall through to
            # SessionAuthentication or other backends
            return None

        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except Exception as e:
            logger.warning(f"Firebase token verification failed: {e}")
            raise exceptions.AuthenticationFailed('Invalid or expired Firebase token.')

        firebase_uid = decoded_token.get('uid')
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')

        if not firebase_uid:
            raise exceptions.AuthenticationFailed('Firebase token missing UID.')

        # Get or create the Django user
        from apps.accounts.models import User, UserProfile

        user, created = User.objects.get_or_create(
            firebase_uid=firebase_uid,
            defaults={
                'username': firebase_uid[:30],
                'email': email,
                'first_name': name.split(' ')[0] if name else '',
                'last_name': ' '.join(name.split(' ')[1:]) if name else '',
            }
        )

        if created:
            # Auto-create an empty profile for new users
            UserProfile.objects.create(user=user)
            logger.info(f"New user created: {user.email} (Firebase UID: {firebase_uid})")

        return (user, decoded_token)
