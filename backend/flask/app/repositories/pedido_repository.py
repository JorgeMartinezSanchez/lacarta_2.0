from sqlalchemy import select

from ..models import Pedido
from .repository import Repository


class PedidoRepository(Repository):
    model = Pedido
    default_order = (Pedido.fecha.desc(), Pedido.id.desc())

    def listar_por_cliente(self, cliente):
        """Mis pedidos: solo los del sub indicado."""
        return self._listar(Pedido.cliente == cliente)

    def get_de_cliente(self, pedido_id, cliente):
        """El pedido solo si es de ese cliente; si es de otro devuelve None (-> 404)."""
        query = select(Pedido).where(Pedido.id == pedido_id, Pedido.cliente == cliente)
        return self.session.scalar(query)

    def listar_activos(self, estados):
        """Cola de la cocina: los más antiguos primero."""
        query = (select(Pedido)
                 .where(Pedido.estado.in_(estados))
                 .order_by(Pedido.fecha, Pedido.id))
        return self.session.scalars(query).all()

    def get_para_actualizar(self, pedido_id):
        """SELECT ... FOR UPDATE: bloquea la fila hasta el commit.

        Si dos personas de cocina pulsan "Avanzar" a la vez, la segunda espera
        a que termine la primera y luego ve el estado ya actualizado.
        """
        return self.session.get(Pedido, pedido_id, with_for_update=True)
