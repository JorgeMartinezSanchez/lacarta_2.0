from flask import session, url_for

from ..errors import error_json
from .errors import AuthError


def handle_auth_error(err: AuthError):
    """401 (sin sesión o token inválido), 400 y 403 como JSON.

    En el 401 se incluye login_url: el frontend decide cuándo llevar al
    usuario a Auth0 (redirigir solo podría rebotar entre Flask y Auth0 sin fin
    si el token se rechazara por un error de configuración).
    """
    extra = {}
    if err.status_code == 401:
        session.pop("access_token", None)  # expired or invalid: useless now
        extra["login_url"] = url_for("auth.login")
    return error_json(err.error["code"], err.error["description"], err.status_code, **extra)
