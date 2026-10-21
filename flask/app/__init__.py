# app/__init__.py
from flask import Flask, redirect, url_for, render_template
from .config import Config
from .extensions import db


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(config_class)

    db.init_app(app)                       # ← lo que faltaba

    from . import models                   # noqa: F401  (registra los modelos)
    from .routes import bp as restaurantes_bp
    from .auth.routes import bp as auth_bp
    from .auth import AuthError
    from .auth.handlers import handle_auth_error
    
    app.register_error_handler(AuthError, handle_auth_error)
    app.register_blueprint(restaurantes_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def home():
        return redirect(url_for("restaurantes.listar_restaurantes"))

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errores/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errores/500.html"), 500

    return app