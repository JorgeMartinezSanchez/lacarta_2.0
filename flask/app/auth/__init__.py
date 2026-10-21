"""Auth0 login for a Flask app with templates, plus the course's decorators.
Auth0 runs the login page, stores the users and assigns their roles. Flask
receives the result on /auth/callback (Authorization Code flow, through
Authlib) and keeps the access token in the signed session cookie.
Follows the structure of the Identity and Access Management course:
AuthError -> error with its HTTP status code
get_token_from_session -> the access token saved at login
verify_decode_jwt -> RS256 signature with Auth0's public keys,
plus expiry, audience and issuer
check_permissions -> 403 when the permission is missing
requires_auth -> decorator that chains the three checks
"""
from .decorators import check_permissions, current_user, get_token_from_session, requires_auth
from .errors import AuthError
from .tokens import verify_decode_jwt

__all__ = [
    "AuthError",
    "check_permissions",
    "current_user",
    "get_token_from_session",
    "requires_auth",
    "verify_decode_jwt",
]