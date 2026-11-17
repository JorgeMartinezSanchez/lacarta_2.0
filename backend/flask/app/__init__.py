import logging
import os

from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Config
from .extensions import JSONProvider, db

def create_app(config_class=Config):
    # Logs a la consola (docker compose logs flask). Nivel con LOG_LEVEL=DEBUG|INFO|WARNING...
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    app = Flask(__name__)
    app.json = JSONProvider(app)  # jsonify: fechas ISO 8601 y tildes sin escapar
    app.config.from_object(config_class)
    for key in ("AUTH0_DOMAIN", "AUTH0_AUDIENCE", "AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET"):
        if not app.config[key]:
            raise RuntimeError(f"{key} is not set. Copy .env.example to .env and fill in your Auth0 values.")
    
    if app.config["BEHIND_PROXY"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)

    from . import models # noqa: F401 (registers the tables for migrations)
    from .auth import AuthError
    from .auth.handlers import handle_auth_error
    from .auth.oauth import init_auth0
    from .auth.routes import bp as auth_bp
    from .auth.tokens import jwks_client

    from .errors import register_error_handlers

    from .routes import restaurantes_bp, platos_bp, pedidos_bp, cocina_bp, empleados_bp

    init_auth0(app)
    # One key client per app, so its cache lives as long as the process.
    app.extensions["auth0_jwks"] = jwks_client(app.config["AUTH0_DOMAIN"])

    app.register_blueprint(restaurantes_bp)
    app.register_blueprint(platos_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(cocina_bp)
    app.register_blueprint(empleados_bp)

    app.register_blueprint(auth_bp)
    app.register_error_handler(AuthError, handle_auth_error)
    register_error_handlers(app)

    @app.get('/health')
    def health():
        return jsonify(status="ok")

    @app.get('/')
    def inicio():
        # Índice de la API. Cuando el frontend esté detrás de Nginx, "/" será suyo.
        return jsonify(
            nombre="La Carta API",
            recursos=["/restaurantes/", "/platos/", "/pedidos/", "/cocina/",
                      "/empleados/", "/auth/me"],
        )

    return app