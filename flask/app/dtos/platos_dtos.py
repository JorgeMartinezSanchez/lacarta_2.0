@dataclass(frozen=True)
class PlatosDTO_Output:
    id: int
    restaurante_id: int
    nombre: str
    precio: float
    disponible: bool

@dataclass(frozen=True)
class PlatosDTO_Input:
    restaurante_id: int
    nombre: str
    precio: float
    disponible: bool