from .base import EstadoPedido
from .entregado import Entregado


class EnPreparacion(EstadoPedido):
    nombre = "en preparación"  # igual que en los templates

    def entregar(self, pedido):
        self._cambiar(pedido, Entregado)

    def cancelar(self, pedido):
        # Regla 7: una vez que cocina empezó, el cliente ya no puede cancelar.
        self._denegar("cancelar", "El pedido ya se está preparando y no se puede cancelar.")
