from functools import wraps

from flask import request, jsonify

from .errors import AuthError
from .tokens import verify_decode_jwt

def get_token_auth_header():

    auth = request.headers.get("Authorization", None).strip()

    if not auth:
        raise AuthError(
            {"code": "authorization_header_missing",
             "description": "Authorization header is expected."
            }, 401)

    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthError(
            {"code": "invalid_header",
             "description": "Authorization header must start with Bearer."
            }, 401)

    if len(parts) == 1:
        raise AuthError(
            {"code": "invalid_header",
             "description": "Token not found."
            }, 401)
    if len(parts) > 2:
        raise AuthError(
            {"code": "invalid_header",
             "description": "Authorization header must be Bearer token."
            }, 401)
    return parts[1]

def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_auth_header()
        try:
            payload = verify_decode_jwt(token)
        except AuthError as e:
            return jsonify(e.error), e.status_code
        return f(payload, *args, **kwargs)
    
    return wrapper