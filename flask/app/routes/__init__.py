from flask import Flask
from .restaurantes import bp as restaurantes_bp
from .platos import bp as platos_bp
from .pedidos import bp as pedidos_bp
from .item_pedido import bp as items_bp

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config)

    __all__ = ["restaurantes_bp", "platos_bp", "pedidos_bp", "items_bp"]

    return app