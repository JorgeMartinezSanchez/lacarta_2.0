from datetime import datetime, timedelta, timezone
import jwt
from flask import current_app

from .errors import AuthError

ALGORITHM = "HS256"

def create_access_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "iat": now,
        "exp": now + timedelta(minutes=current_app.config["JWT_EXPIRES_MINUTES"]),
        "iss": current_app.config["JWT_ISSUER"],
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm=ALGORITHM)

def verify_decode_jwt(token):
    try:
        return jwt.decode(token, 
                          current_app.config["JWT_SECRET_KEY"], 
                          algorithms=[ALGORITHM], 
                          issuer=current_app.config["JWT_ISSUER"],
                          options={"require": ["exp", "iss", "sub"]}
                          )
    except jwt.ExpiredSignatureError:
        raise AuthError({"code": "token_expired", "description": "Token has expired."}, 401)
    except jwt.InvalidIssuerError:
        raise AuthError({"code": "invalid_issuer", "description": "Invalid token issuer."}, 401)
 