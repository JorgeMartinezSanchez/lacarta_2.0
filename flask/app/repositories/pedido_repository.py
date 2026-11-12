from ..models import Pedido
from .repository import Repository


class PedidoRepository(Repository):
    model = Pedido
    default_order = (Pedido.fecha.desc(),)
