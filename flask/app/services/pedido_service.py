import logging
from datetime import date

from ..dtos.pedidos_dtos import PedidosDTO_Input, PedidosDTO_Output
from ..errors import BusinessRuleError, NotFoundError
from ..models import Pedido
from ..repositories.pedido_repository import PedidoRepository
from ..repositories.restaurantes_repository import RestauranteRepository
from ..state.pedidos import Cancelado, Pendiente, cambiar_estado, estado_de

logger = logging.getLogger(__name__)


class PedidosService:
    def __init__(self, pedidos_repo: PedidoRepository, restaurantes_repo: RestauranteRepository):
        self.pedidos_repo = pedidos_repo
        self.restaurantes_repo = restaurantes_repo  # para validar que el restaurante exista

    # --- lectura ---------------------------------------------------------

    def get_all_pedidos(self) -> list[PedidosDTO_Output]:
        try:
            pedidos = self.pedidos_repo.getAll()
            return [self._to_dto(p) for p in pedidos]
        finally:
            self.pedidos_repo.close()

    def get_pedido(self, pedido_id: int) -> PedidosDTO_Output:
        try:
            return self._to_dto(self._find(pedido_id))
        finally:
            self.pedidos_repo.close()

    # --- escritura -------------------------------------------------------

    def create_pedido(self, newPedido: PedidosDTO_Input) -> PedidosDTO_Output:
        """Crea un pedido vacío.

        estado, fecha y total NO se toman del DTO: los decide el servidor.
        Todo pedido nace 'pendiente', con la fecha de hoy y sin total
        (el total lo calcula ItemPedidosService al agregar ítems).
        """
        try:
            self._validar_restaurante(newPedido.restaurante_id)

            pedido = self.pedidos_repo.create(Pedido(
                restaurante_id=newPedido.restaurante_id,
                estado=Pendiente.nombre,
                fecha=date.today(),
                total=None,
            ))
            self.pedidos_repo.commit()

            return self._to_dto(pedido)
        except BusinessRuleError as e:
            # Error esperado (validación / regla de negocio): lo ve el usuario.
            self.pedidos_repo.rollback()
            logger.warning("create_pedido(newPedido=%r) rechazado: %s", newPedido, e)
            raise
        except Exception:
            # Error inesperado (base de datos, bug): traza completa en el log.
            self.pedidos_repo.rollback()
            logger.exception("create_pedido(newPedido=%r) falló", newPedido)
            raise
        finally:
            self.pedidos_repo.close()

    def update_pedido(self, pedido_id: int, pedidoData: PedidosDTO_Input) -> PedidosDTO_Output:
        """Cambia el restaurante y/o el estado.

        - El estado pasa por el patrón State: solo se permiten transiciones válidas.
        - El restaurante solo se puede cambiar si el pedido es modificable y no tiene ítems.
        - fecha y total del DTO se ignoran.
        """
        try:
            pedido = self._find(pedido_id)

            if pedidoData.restaurante_id != pedido.restaurante_id:
                if not estado_de(pedido).puede_modificarse():
                    raise BusinessRuleError(f"Un pedido {pedido.estado} ya no se puede modificar.")
                if pedido.items:
                    raise BusinessRuleError("No se puede cambiar el restaurante de un pedido con ítems.")
                self._validar_restaurante(pedidoData.restaurante_id)
                pedido = self.pedidos_repo.update(pedido, restaurante_id=pedidoData.restaurante_id)

            nuevo_estado = (pedidoData.estado or "").strip()
            if nuevo_estado:
                cambiar_estado(pedido, nuevo_estado)  # lanza TransicionInvalida si no se puede

            self.pedidos_repo.commit()

            return self._to_dto(pedido)
        except BusinessRuleError as e:
            # Error esperado (validación / regla de negocio): lo ve el usuario.
            self.pedidos_repo.rollback()
            logger.warning("update_pedido(pedido_id=%r, pedidoData=%r) rechazado: %s", pedido_id, pedidoData, e)
            raise
        except Exception:
            # Error inesperado (base de datos, bug): traza completa en el log.
            self.pedidos_repo.rollback()
            logger.exception("update_pedido(pedido_id=%r, pedidoData=%r) falló", pedido_id, pedidoData)
            raise
        finally:
            self.pedidos_repo.close()

    def delete_pedido(self, pedido_id: int) -> None:
        """Solo se borran pedidos pendientes o cancelados (los demás son historial)."""
        try:
            pedido = self._find(pedido_id)

            if pedido.estado not in (Pendiente.nombre, Cancelado.nombre):
                raise BusinessRuleError(f"No se puede eliminar un pedido {pedido.estado}.")

            # cascade="all, delete-orphan" del modelo borra también sus ítems
            self.pedidos_repo.delete(pedido)
            self.pedidos_repo.commit()
        except BusinessRuleError as e:
            # Error esperado (validación / regla de negocio): lo ve el usuario.
            self.pedidos_repo.rollback()
            logger.warning("delete_pedido(pedido_id=%r) rechazado: %s", pedido_id, e)
            raise
        except Exception:
            # Error inesperado (base de datos, bug): traza completa en el log.
            self.pedidos_repo.rollback()
            logger.exception("delete_pedido(pedido_id=%r) falló", pedido_id)
            raise
        finally:
            self.pedidos_repo.close()

    # --- ayudantes privados ----------------------------------------------

    def _find(self, pedido_id: int) -> Pedido:
        pedido = self.pedidos_repo.getOne(pedido_id)
        if pedido is None:
            raise NotFoundError(f"No existe el pedido {pedido_id}.")
        return pedido

    def _validar_restaurante(self, restaurante_id: int) -> None:
        if not restaurante_id or self.restaurantes_repo.getOne(restaurante_id) is None:
            raise BusinessRuleError("Debes elegir un restaurante válido.")

    @staticmethod
    def _to_dto(p: Pedido) -> PedidosDTO_Output:
        return PedidosDTO_Output(
            id=p.id,
            restaurante_id=p.restaurante_id,
            estado=p.estado,
            fecha=p.fecha,
            total=float(p.total) if p.total is not None else None,
        )
