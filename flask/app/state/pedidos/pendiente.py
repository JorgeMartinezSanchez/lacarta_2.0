from .base import EstadoPedido
from .cancelado import Cancelado
from .en_preparacion import EnPreparacion


class Pendiente(EstadoPedido):
    nombre = "pendiente"
    etiqueta = "Pendiente"

    def preparar(self, pedido):
        self._cambiar(pedido, EnPreparacion)

    def cancelar(self, pedido):
        self._cambiar(pedido, Cancelado)

    def puede_modificarse(self):
        return True
