from dataclasses import dataclass

@dataclass(frozen=True)
class PlatosDTO_Output:
    id: int
    restaurante_id: int
    nombre: str
    precio: float
    disponible: bool
    restaurante_nombre: str | None = None 
@dataclass(frozen=True)
class PlatosDTO_Input:
    restaurante_id: int
    nombre: str
    precio: float
    disponible: bool