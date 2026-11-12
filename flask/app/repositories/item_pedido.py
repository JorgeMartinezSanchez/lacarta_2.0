from ..models import ItemPedido
from .repository import Repository


class ItemPedidoRepository(Repository):
    model = ItemPedido
    default_order = (ItemPedido.id,)
