from decimal import Decimal

from ..dtos.item_pedido_dtos import ItemPedidosDTO_Input, ItemPedidosDTO_Output
from ..errors import BusinessRuleError, NotFoundError
from ..models import ItemPedido, Pedido, Plato
from ..repositories.item_pedido import ItemPedidoRepository
from ..repositories.pedido_repository import PedidoRepository
from ..repositories.plato_repository import PlatoRepository
from ..state.pedidos import estado_de


class ItemPedidosService:
    def __init__(
        self,
        items_repo: ItemPedidoRepository,
        pedidos_repo: PedidoRepository,
        platos_repo: PlatoRepository,
    ):
        self.items_repo = items_repo
        self.pedidos_repo = pedidos_repo
        self.platos_repo = platos_repo

    # --- lectura ---------------------------------------------------------

    def get_all_items(self) -> list[ItemPedidosDTO_Output]:
        try:
            items = self.items_repo.getAll()
            return [self._to_dto(i) for i in items]
        finally:
            self.items_repo.close()

    def get_item(self, item_id: int) -> ItemPedidosDTO_Output:
        try:
            return self._to_dto(self._find(item_id))
        finally:
            self.items_repo.close()

    # --- escritura -------------------------------------------------------

    def create_item(self, newItem: ItemPedidosDTO_Input) -> ItemPedidosDTO_Output:
        """Agrega un plato a un pedido.

        precio_unitario y restaurante_id NO se toman del DTO: se copian del
        plato, para que el cliente no pueda fijar su propio precio.
        """
        try:
            pedido = self._find_pedido_modificable(newItem.pedido_id)
            plato = self._find_plato_para(pedido, newItem.plato_id)
            cantidad = self._validar_cantidad(newItem.cantidad)

            item = self.items_repo.create(ItemPedido(
                pedido_id=pedido.id,
                plato_id=plato.id,
                cantidad=str(cantidad),          # la columna es String (ver nota)
                precio_unitario=plato.precio,    # precio del momento del pedido
                restaurante_id=plato.restaurante_id,
            ))
            self._recalcular_total(pedido)
            self.items_repo.commit()

            return self._to_dto(item)
        except Exception:
            self.items_repo.rollback()
            raise
        finally:
            self.items_repo.close()

    def update_item(self, item_id: int, itemData: ItemPedidosDTO_Input) -> ItemPedidosDTO_Output:
        """Cambia la cantidad y/o el plato. El ítem no se puede mover a otro pedido."""
        try:
            item = self._find(item_id)
            pedido = self._find_pedido_modificable(item.pedido_id)

            if itemData.pedido_id != item.pedido_id:
                raise BusinessRuleError("Un ítem no se puede mover a otro pedido.")

            campos = {"cantidad": str(self._validar_cantidad(itemData.cantidad))}
            if itemData.plato_id != item.plato_id:
                plato = self._find_plato_para(pedido, itemData.plato_id)
                campos.update(plato_id=plato.id, precio_unitario=plato.precio)

            item = self.items_repo.update(item, **campos)
            self._recalcular_total(pedido)
            self.items_repo.commit()

            return self._to_dto(item)
        except Exception:
            self.items_repo.rollback()
            raise
        finally:
            self.items_repo.close()

    def delete_item(self, item_id: int) -> None:
        try:
            item = self._find(item_id)
            pedido = self._find_pedido_modificable(item.pedido_id)

            self.items_repo.delete(item)
            self._recalcular_total(pedido)
            self.items_repo.commit()
        except Exception:
            self.items_repo.rollback()
            raise
        finally:
            self.items_repo.close()

    # --- ayudantes privados ----------------------------------------------

    def _find(self, item_id: int) -> ItemPedido:
        item = self.items_repo.getOne(item_id)
        if item is None:
            raise NotFoundError(f"No existe el ítem {item_id}.")
        return item

    def _find_pedido_modificable(self, pedido_id: int) -> Pedido:
        pedido = self.pedidos_repo.getOne(pedido_id)
        if pedido is None:
            raise NotFoundError(f"No existe el pedido {pedido_id}.")
        if not estado_de(pedido).puede_modificarse():  # regla 12, vía patrón State
            raise BusinessRuleError(f"Un pedido {pedido.estado} ya no se puede modificar.")
        return pedido

    def _find_plato_para(self, pedido: Pedido, plato_id: int) -> Plato:
        plato = self.platos_repo.getOne(plato_id)
        if plato is None:
            raise BusinessRuleError("Debes elegir un plato válido.")
        if plato.restaurante_id != pedido.restaurante_id:
            raise BusinessRuleError("El plato no pertenece al restaurante del pedido.")
        if not plato.disponible:
            raise BusinessRuleError(f"El plato '{plato.nombre}' no está disponible.")
        return plato

    @staticmethod
    def _validar_cantidad(cantidad) -> int:
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            raise BusinessRuleError("La cantidad debe ser un número entero.") from None
        if cantidad <= 0:
            raise BusinessRuleError("La cantidad debe ser mayor a 0.")
        return cantidad

    def _recalcular_total(self, pedido: Pedido) -> None:
        # refresh recarga pedido.items desde la base (ya con el INSERT/UPDATE/DELETE del flush)
        self.pedidos_repo.refresh(pedido)
        total = sum(
            (Decimal(i.precio_unitario) * int(i.cantidad) for i in pedido.items),
            Decimal("0"),
        )
        self.pedidos_repo.update(pedido, total=total if pedido.items else None)

    @staticmethod
    def _to_dto(i: ItemPedido) -> ItemPedidosDTO_Output:
        return ItemPedidosDTO_Output(
            id=i.id,
            pedido_id=i.pedido_id,
            plato_id=i.plato_id,
            cantidad=int(i.cantidad),
            precio_unitario=float(i.precio_unitario),
            restaurante_id=i.restaurante_id,
        )
