import logging
from datetime import date
from decimal import Decimal

from ..dtos.item_pedido_dtos import ItemPedidosDTO_Output
from ..dtos.pedidos_dtos import NuevoPedidoDTO, PedidosDTO_Output
from ..errors import BusinessRuleError, NotFoundError
from ..models import ItemPedido, Pedido
from ..repositories.pedido_repository import PedidoRepository
from ..repositories.plato_repository import PlatoRepository
from ..repositories.restaurantes_repository import RestauranteRepository
from ..state.pedidos import ACTIVOS, DESTINOS_COCINA, Pendiente, cambiar_estado, estado_de

logger = logging.getLogger(__name__)

CANTIDAD_MIN, CANTIDAD_MAX = 1, 20  # R1.5 (la base lo refuerza con un CHECK)


class PedidosService:
    def __init__(
        self,
        pedidos_repo: PedidoRepository,
        restaurantes_repo: RestauranteRepository,
        platos_repo: PlatoRepository,
    ):
        self.pedidos_repo = pedidos_repo
        self.restaurantes_repo = restaurantes_repo
        self.platos_repo = platos_repo

    # =====================================================================
    # Cliente
    # =====================================================================

    def create_pedido(self, nuevo: NuevoPedidoDTO, cliente: str) -> PedidosDTO_Output:
        """R1: crea el pedido con TODOS sus ítems en una sola transacción.

        - cliente: el 'sub' del token (lo pasa la ruta), nunca un dato del formulario.
        - precio_unitario se copia del plato (precio congelado) y el total lo calcula
          el servidor: del formulario solo se usan plato_id y cantidad.
        - Si UN ítem es inválido se rechaza el pedido completo: se valida todo antes de
          escribir y hay un único commit; ante cualquier error, rollback.
        """
        try:
            if not cliente:
                raise BusinessRuleError("No se pudo identificar al cliente.")
            
            if self.restaurantes_repo.getOne(nuevo.restaurante_id) is None:
                raise NotFoundError(f"No existe el restaurante {nuevo.restaurante_id}.")
            
            if not nuevo.items:
                raise BusinessRuleError("Elige al menos un plato.")

            # 1. Validar todos los ítems (todavía no se escribe nada)
            items, total, vistos = [], Decimal("0"), set()
            for item in nuevo.items:
                if item.plato_id in vistos:
                    raise BusinessRuleError("Un plato aparece repetido en el pedido.")
                vistos.add(item.plato_id)

                plato = self.platos_repo.getOne(item.plato_id)
                if plato is None:
                    raise BusinessRuleError(f"El plato {item.plato_id} no existe.")
                if plato.restaurante_id != nuevo.restaurante_id:
                    raise BusinessRuleError(f"El plato '{plato.nombre}' es de otro restaurante.")
                if not plato.disponible:
                    raise BusinessRuleError(f"El plato '{plato.nombre}' no está disponible.")
                cantidad = self._validar_cantidad(item.cantidad, plato.nombre)

                items.append(ItemPedido(
                    plato_id=plato.id,
                    cantidad=cantidad,
                    precio_unitario=plato.precio,       # R1.3 precio congelado
                    restaurante_id=plato.restaurante_id,
                ))
                total += plato.precio * cantidad         # R1.4 total del servidor

            # 2. Escribir pedido + ítems (cascade) y confirmar una sola vez
            pedido = self.pedidos_repo.create(Pedido(
                cliente=cliente,
                restaurante_id=nuevo.restaurante_id,
                estado=Pendiente.nombre,
                fecha=date.today(),
                total=total,
                items=items,
            ))
            self.pedidos_repo.commit()

            return self._to_dto(pedido, con_items=True)
        except BusinessRuleError as e:
            self.pedidos_repo.rollback()
            logger.warning("create_pedido(nuevo=%r, cliente=%r) rechazado: %s", nuevo, cliente, e)
            raise
        except Exception:
            self.pedidos_repo.rollback()
            logger.exception("create_pedido(nuevo=%r, cliente=%r) falló", nuevo, cliente)
            raise
        finally:
            self.pedidos_repo.close()

    def get_mis_pedidos(self, cliente: str) -> list[PedidosDTO_Output]:
        try:
            return [self._to_dto(p) for p in self.pedidos_repo.listar_por_cliente(cliente)]
        finally:
            self.pedidos_repo.close()

    def get_mi_pedido(self, pedido_id: int, cliente: str) -> PedidosDTO_Output:
        """R2.6: el pedido de otro cliente se trata igual que uno inexistente (404)."""
        try:
            return self._to_dto(self._find_de_cliente(pedido_id, cliente), con_items=True)
        finally:
            self.pedidos_repo.close()

    def cancelar(self, pedido_id: int, cliente: str) -> PedidosDTO_Output:
        """pendiente -> cancelado, solo el cliente dueño (tabla de estados)."""
        try:
            pedido = self._find_de_cliente(pedido_id, cliente)
            estado_de(pedido).cancelar(pedido)   # el patrón State rechaza si no está pendiente
            self.pedidos_repo.commit()
            return self._to_dto(pedido)
        except BusinessRuleError as e:
            self.pedidos_repo.rollback()
            logger.warning("cancelar(pedido_id=%r, cliente=%r) rechazado: %s", pedido_id, cliente, e)
            raise
        except Exception:
            self.pedidos_repo.rollback()
            logger.exception("cancelar(pedido_id=%r, cliente=%r) falló", pedido_id, cliente)
            raise
        finally:
            self.pedidos_repo.close()

    # =====================================================================
    # Cocina
    # =====================================================================

    def get_cola_cocina(self) -> list[PedidosDTO_Output]:
        """Pedidos activos (pendiente, en preparación, listo), los más antiguos primero."""
        try:
            return [self._to_dto(p, con_items=True) for p in self.pedidos_repo.listar_activos(ACTIVOS)]
        finally:
            self.pedidos_repo.close()

    def avanzar(self, pedido_id: int, nuevo_estado: str) -> PedidosDTO_Output:
        """pendiente -> en_preparacion -> listo -> entregado (rol cocina).

        La cocina no puede cancelar ni retroceder: solo acepta destinos de cocina,
        y el patrón State rechaza los saltos (p. ej. listo -> pendiente).
        """
        try:
            nuevo_estado = (nuevo_estado or "").strip()
            if nuevo_estado not in DESTINOS_COCINA:
                raise BusinessRuleError(f"La cocina no puede pasar un pedido a '{nuevo_estado}'.")

            pedido = self.pedidos_repo.get_para_actualizar(pedido_id)  # SELECT ... FOR UPDATE
            if pedido is None:
                raise NotFoundError(f"No existe el pedido {pedido_id}.")

            cambiar_estado(pedido, nuevo_estado)  # lanza TransicionInvalida si no se puede
            self.pedidos_repo.commit()
            return self._to_dto(pedido)
        except BusinessRuleError as e:
            self.pedidos_repo.rollback()
            logger.warning("avanzar(pedido_id=%r, nuevo_estado=%r) rechazado: %s", pedido_id, nuevo_estado, e)
            raise
        except Exception:
            self.pedidos_repo.rollback()
            logger.exception("avanzar(pedido_id=%r, nuevo_estado=%r) falló", pedido_id, nuevo_estado)
            raise
        finally:
            self.pedidos_repo.close()

    # =====================================================================
    # Ayudantes privados
    # =====================================================================

    def _find_de_cliente(self, pedido_id: int, cliente: str) -> Pedido:
        pedido = self.pedidos_repo.get_de_cliente(pedido_id, cliente)
        if pedido is None:  # no existe O es de otro cliente: misma respuesta
            raise NotFoundError(f"No existe el pedido {pedido_id}.")
        return pedido

    @staticmethod
    def _validar_cantidad(cantidad, nombre_plato: str) -> int:
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            raise BusinessRuleError(f"La cantidad de '{nombre_plato}' debe ser un número entero.") from None
        if not CANTIDAD_MIN <= cantidad <= CANTIDAD_MAX:
            raise BusinessRuleError(
                f"La cantidad de '{nombre_plato}' debe estar entre {CANTIDAD_MIN} y {CANTIDAD_MAX}."
            )
        return cantidad

    @staticmethod
    def _to_dto(p: Pedido, con_items: bool = False) -> PedidosDTO_Output:
        items = ()
        if con_items:
            items = tuple(
                ItemPedidosDTO_Output(
                    id=i.id,
                    pedido_id=i.pedido_id,
                    plato_id=i.plato_id,
                    cantidad=i.cantidad,
                    precio_unitario=float(i.precio_unitario),
                    restaurante_id=i.restaurante_id,
                    plato_nombre=i.plato.nombre,
                )
                for i in p.items
            )
        return PedidosDTO_Output(
            id=p.id,
            restaurante_id=p.restaurante_id,
            estado=p.estado,
            fecha=p.fecha,
            total=float(p.total),
            restaurante_nombre=p.restaurante.nombre,
            cliente=p.cliente,
            items=items,
        )
