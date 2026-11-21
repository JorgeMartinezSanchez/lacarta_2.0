"""Login con Auth0.

/auth/login y /auth/callback siguen siendo redirecciones: el navegador tiene
que NAVEGAR a Auth0 y volver (no se puede hacer con fetch). El resto responde
JSON para el frontend.
"""
from urllib.parse import urlencode

from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, current_app, jsonify, redirect, request, session, url_for

from ..errors import error_json
from .decorators import current_user
from .oauth import auth0

bp = Blueprint("auth", __name__, url_prefix="/auth")


def safe_next(target):
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return url_for("inicio")


@bp.route("/login")
def login():
    """Send the browser to Auth0's login page. ?next=/ruta vuelve ahí al terminar."""
    session["next"] = safe_next(request.args.get("next"))

    # Lee el parámetro de la URL para forzar el login
    force_login = request.args.get("force") == "1"

    return auth0().authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True),
        audience=current_app.config["AUTH0_AUDIENCE"],
        # Añade prompt solo si se solicita explícitamente
        prompt="login" if force_login else None
    )


@bp.route("/callback")
def callback():
    try:
        token = auth0().authorize_access_token()
    except OAuthError as err:
        current_app.logger.error("Auth0 callback error: %s - %s", err.error, err.description)
        if err.error == "mismatching_state" and session.get("user"):
            # Callback repetido (p. ej. botón "atrás"): la sesión ya está iniciada.
            return redirect(session.pop("next", None) or url_for("inicio"))
        return error_json("auth0_error", err.description or err.error, 400)

    next_url = session.pop("next", None) or url_for("inicio")

    profile = token.get("userinfo") or {}
    session.clear()  # a new login starts a new session: nothing from before survives
    session["access_token"] = token["access_token"]
    session["user"] = {"name": profile.get("name") or profile.get("email"),
                       "email": profile.get("email")}
    return redirect(next_url)


@bp.get("/me")
def me():
    """Quién inició sesión y qué permisos tiene ({"usuario": null} si nadie).

    Sirve al frontend para mostrar el nombre y ocultar botones; ocultar es solo
    UX: el decorador de cada ruta es lo que la protege.
    """
    return jsonify(usuario=current_user())


@bp.post("/logout")
def logout():
    """Cierra la sesión de Flask y devuelve la URL para cerrar también la de Auth0.

    El frontend hace: location.href = respuesta.logout_url
    """
    session.clear()
    params = urlencode({
        # Debe estar en "Allowed Logout URLs" de Auth0.
        "returnTo": url_for("inicio", _external=True),   # "/" = el frontend (Nginx)
        "client_id": current_app.config["AUTH0_CLIENT_ID"],
    })
    return jsonify(logout_url=f"https://{current_app.config['AUTH0_DOMAIN']}/v2/logout?{params}")
