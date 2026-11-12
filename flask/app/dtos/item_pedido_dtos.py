from datetime import date

@dataclass(frozen=True)
class ItemPedidosDTO_Output:
  id: int
  pedido_id: int
  plato_id: int
  cantidad: int
  precio_unitario: float
  restaurante_id: int

@dataclass(frozen=True)
class ItemPedidosDTO_Input:
  pedido_id: int
  plato_id: int
  cantidad: int
  precio_unitario: float
  restaurante_id: int