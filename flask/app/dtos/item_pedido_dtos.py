from dataclasses import dataclass

@dataclass(frozen=True)
class ItemPedidosDTO_Output:
  id: int
  pedido_id: int
  plato_id: int
  cantidad: int
  precio_unitario: float
  restaurante_id: int
  plato_nombre: str | None = None  # para mostrar en pantalla

@dataclass(frozen=True)
class ItemPedidosDTO_Input:
  pedido_id: int
  plato_id: int
  cantidad: int
  # El servicio ignora estos dos: los copia del plato.
  precio_unitario: float | None = None
  restaurante_id: int | None = None