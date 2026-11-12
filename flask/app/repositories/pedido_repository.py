from ..models import Pedido
from .repository import Repository


class PedidoRepository(Repository):
    model = Pedido
    default_order = (Pedido.fecha.desc(), Pedido.id.desc())

    def listar_por_estado(self, estado):
        return self._listar(Pedido.estado == estado)
