# app/__init__.py
from flask import Flask, redirect, url_for, render_template
from .config import Config


def create_app(config_class=Config):
    # static/ está en flask/static, fuera de app/, por eso se indica la ruta
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(config_class)

    # Blueprints
    from .routes import bp as restaurantes_bp
    from .auth.routes import bp as auth_bp

    app.register_blueprint(restaurantes_bp)   # /restaurantes/...
    app.register_blueprint(auth_bp)           # /auth/...

    # Home
    @app.route("/")
    def home():
        return redirect(url_for("restaurantes.listar_restaurantes"))

    # Manejadores de errores (usan tus plantillas errores/404.html y 500.html)
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errores/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errores/500.html"), 500

    return app