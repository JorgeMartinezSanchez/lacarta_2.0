from .base import EstadoPedido
from .entregado import Entregado


class Listo(EstadoPedido):
    nombre = "listo"
    etiqueta = "Listo"

    def entregar(self, pedido):
        self._cambiar(pedido, Entregado)
