import jwt
from flask import current_app
from .errors import AuthError
# Auth0 signs with its private key (RS256). The API verifies with the public
# key, so it never holds a secret that could forge tokens.
ALGORITHMS = ["RS256"]
def jwks_client(domain):
    """Client for Auth0's public keys at /.well-known/jwks.json.
    It downloads the key set once and keeps it in memory, so a request does
    not wait for Auth0. It downloads again only when a token names a key id
    (`kid`) it has not seen, which is what happens when Auth0 rotates keys.
    """
    return jwt.PyJWKClient(f"https://{domain}/.well-known/jwks.json", cache_keys=True, timeout=5)

def verify_decode_jwt(token):
    """Return the payload of a valid Auth0 token or raise AuthError.
    Same checks as the course: the key matching the token's `kid`, the
    RS256 signature, expiry, audience and issuer.
    """
    domain = current_app.config["AUTH0_DOMAIN"]
    try:
        signing_key = current_app.extensions["auth0_jwks"].get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=ALGORITHMS,
            audience=current_app.config["AUTH0_AUDIENCE"],
            issuer=f"https://{domain}/",
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise AuthError({"code": "token_expired", "description": "Token expired."}, 401)
    
    except (jwt.InvalidAudienceError, jwt.InvalidIssuerError):
        raise AuthError({"code": "invalid_claims", "description": "Incorrect claims. Please, check the audience and issuer."}, 401)
    
    except jwt.PyJWKClientConnectionError:
        # Auth0 could not be reached: our problem, not the user's.
        raise AuthError({"code": "jwks_unavailable", "description": "Unable to fetch the signing keys."}, 503)
    
    except jwt.PyJWKClientError:
        raise AuthError({"code": "invalid_header", "description": "Unable to find the appropriate key."}, 401)
    
    except jwt.InvalidTokenError:
        raise AuthError({"code": "invalid_token", "description": "Invalid token."}, 401)