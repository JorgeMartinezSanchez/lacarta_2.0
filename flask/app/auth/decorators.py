from functools import wraps
from flask import session

from .errors import AuthError
from .tokens import verify_decode_jwt

def get_token_from_session():
    """Return the Auth0 access token saved by /auth/callback.
    The course reads the token from the Authorization header because its
    frontend is a separate JavaScript app. Here the browser talks to Flask
    through links and forms, which cannot send headers, so the token lives in
    the signed session cookie instead.
    """
    token = session.get("access_token")
    if not token:
        raise AuthError({"code": "not_signed_in", "description": "Please sign in to continue."}, 401)
    return token

def check_permissions(permission, payload):
    if "permissions" not in payload:
        raise AuthError({"code": "invalid_claims", "description": "Permissions not included in the token."}, 400)
    if permission and permission not in payload["permissions"]:
        raise AuthError({"code": "forbidden", "description": "You do not have permission to do this."}, 403)
    return True
   

def requires_auth(permission=""):
    """Decorator factory: `@requires_auth('delete:todos')`.
    Three filters, in order: is there a token (401), is it valid (401),
    does it carry the permission (403). The decoded payload is passed to the
    view as its first argument, exactly like the course example.
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_from_session()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator

def current_user():
    """The signed-in user for templates, or None. Never raises.
    The name comes from the login profile; the permissions come from the
    verified access token, the same place the decorator reads them.
    """
    token = session.get("access_token")
    if not token:
        return None
    try:
        payload = verify_decode_jwt(token)
    except AuthError:
        return None
    profile = session.get("user", {})
    return {
        "name": profile.get("name"),
        "email": profile.get("email"),
        "sub": payload["sub"],
        "permissions": payload.get("permissions", []),
    }