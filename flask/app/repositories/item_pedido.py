from ..models import ItemPedido
from .repository import Repository


class ItemPedidoRepository(Repository):
    model = ItemPedido
    default_order = (ItemPedido.id,)

    def listar_por_pedido(self, pedido_id):
        return self._listar(ItemPedido.pedido_id == pedido_id)
