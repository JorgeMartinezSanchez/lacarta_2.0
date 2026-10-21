from authlib.integrations.flask_client import OAuth
from flask import app, current_app

def init_auth0(app):
    """Register Auth0 as an OpenID Connect provider for this app.
    Authlib reads every Auth0 URL (authorize, token, keys) from the tenant's
    discovery document, so only the domain has to be configured. Each app
    gets its own registry, so two app instances never share a client.
    """
    oauth = OAuth(app)
    oauth.register(
        "auth0",
        client_id=app.config["AUTH0_CLIENT_ID"],
        client_secret=app.config["AUTH0_CLIENT_SECRET"],
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url=f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration",
    )

def auth0():
    """The Auth0 client of the current app."""
    return current_app.extensions["authlib.integrations.flask_client"].auth0