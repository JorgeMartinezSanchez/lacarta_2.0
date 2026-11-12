from datetime import date

@dataclass(frozen=True)
class PedidosDTO_Output:
  id: int
  restaurante_id: int
  estado: str
  fecha: date
  total: float

@dataclass(frozen=True)
class PedidosDTO_Input:
  restaurante_id: int
  estado: str
  fecha: date
  total: float