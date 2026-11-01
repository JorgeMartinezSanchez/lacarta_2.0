from urllib.parse import urlencode
from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, current_app, flash, redirect, request, session, url_for
from .oauth import auth0

bp = Blueprint("auth", __name__, url_prefix="/auth")

def safe_next(target):
    """Only allow redirects to paths inside this site (no open redirect)."""
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return url_for("auth.login")

@bp.route("/login")
def login():
    """Send the browser to Auth0's login page.
    `audience` asks Auth0 for an access token for our API, which carries the
    user's permissions. Authlib adds a random `state` and checks it on the
    way back, so a login started elsewhere cannot be injected.
    """
    session["next"] = safe_next(request.args.get("next"))
    return auth0().authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True),
        audience=current_app.config["AUTH0_AUDIENCE"],
    )

@bp.route("/callback")
def callback():
    try:
        token = auth0().authorize_access_token()
    except OAuthError as err:
        flash(f"Auth0: {err.description or err.error}", "error")
        return redirect(url_for("restaurantes.listar_restaurantes"))  # ✅

    next_url = session.pop("next", None) or url_for("restaurantes.listar_restaurantes")

    profile = token.get("userinfo") or {}
    session.clear() # a new login starts a new session: nothing from before survives
    session["access_token"] = token["access_token"]
    session["user"] = {"name": profile.get("name") or profile.get("email"), "email":
    profile.get("email")}
    return redirect(next_url)

@bp.post("/logout")
def logout():
    session.clear()
    params = urlencode({
        "returnTo": url_for("restaurantes.listar_restaurantes", _external=True),  # ✅
        "client_id": current_app.config["AUTH0_CLIENT_ID"],
    })
    return redirect(f"https://{current_app.config['AUTH0_DOMAIN']}/v2/logout?{params}")