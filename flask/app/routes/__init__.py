from flask import Flask
from .extensions import db
from .blueprints.restaurantes import bp as restaurantes_bp
from .blueprints.platos import bp as platos_bp
from .blueprints.pedidos import bp as pedidos_bp
from .blueprints.items_pedido import bp as items_bp

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    # Orden explícito: pedidos primero (por si en el futuro crece su jerarquía)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(restaurantes_bp)
    app.register_blueprint(platos_bp)
    app.register_blueprint(items_bp)

    return app