from sqlalchemy import select

from ..models import ItemPedido, Plato
from .repository import Repository


class PlatoRepository(Repository):
    model = Plato
    default_order = (Plato.nombre,)

    def listar_por_restaurante(self, restaurante_id):
        return self._listar(Plato.restaurante_id == restaurante_id)

    def esta_en_pedidos(self, plato_id):
        """¿Algún ítem de pedido usa este plato?"""
        query = select(ItemPedido.id).where(ItemPedido.plato_id == plato_id)
        return self.session.scalar(select(query.exists())) or False
