from dataclasses import dataclass, field
from datetime import date

from .item_pedido_dtos import ItemPedidosDTO_Output


@dataclass(frozen=True)
class PedidosDTO_Output:
  id: int
  restaurante_id: int
  estado: str
  fecha: date
  total: float
  restaurante_nombre: str | None = None
  cliente: str | None = None  # sub de Auth0 del dueño
  items: tuple[ItemPedidosDTO_Output, ...] = field(default_factory=tuple)


# --- Entrada para crear un pedido completo (R1.4: solo platos y cantidades) ---

@dataclass(frozen=True)
class ItemNuevoDTO:
  plato_id: int
  cantidad: int | str  # llega del formulario; el servicio la valida (entero de 1 a 20)


@dataclass(frozen=True)
class NuevoPedidoDTO:
  restaurante_id: int
  items: tuple[ItemNuevoDTO, ...]
  # Sin cliente, estado, fecha, precios ni total: todo eso lo decide el servidor.
