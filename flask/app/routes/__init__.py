from .cocina import bp as cocina_bp
from .pedidos import bp as pedidos_bp
from .platos import bp as platos_bp
from .restaurantes import bp as restaurantes_bp

__all__ = ["restaurantes_bp", "platos_bp", "pedidos_bp", "cocina_bp"]
