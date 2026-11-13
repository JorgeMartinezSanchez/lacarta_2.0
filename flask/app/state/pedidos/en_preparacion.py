from .base import EstadoPedido
from .listo import Listo


class EnPreparacion(EstadoPedido):
    nombre = "en_preparacion"
    etiqueta = "En preparación"

    def marcar_listo(self, pedido):
        self._cambiar(pedido, Listo)

    def cancelar(self, pedido):
        # Una vez que cocina empezó, el cliente ya no puede cancelar.
        self._denegar("cancelar", "El pedido ya se está preparando y no se puede cancelar.")
