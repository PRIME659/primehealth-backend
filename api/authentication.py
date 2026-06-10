from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class SessionJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result

        if not hasattr(user, "profile"):
            return user, token

        profile = user.profile

        # Check if account is locked
        if profile.is_locked():
            raise AuthenticationFailed(
                f"Account is locked. Try again after {profile.locked_until.strftime('%H:%M:%S')}."
            )

        # Check session ID
        token_session_id = token.get("session_id")
        if token_session_id and profile.session_id != token_session_id:
            raise AuthenticationFailed(
                "Your session has been terminated. Please log in again."
            )

        return user, token
