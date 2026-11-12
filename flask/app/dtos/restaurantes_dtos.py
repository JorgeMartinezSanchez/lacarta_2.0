from dataclasses import dataclass

@dataclass(frozen=True)
class RestauranteDTO_Output:
    id: int
    nombre: str
    ciudad: str
    direccion: str | None = None
    telefono: str | None = None

@dataclass(frozen=True)
class RestauranteDTO_Input:
    nombre: str
    ciudad: str
    direccion: str | None = None
    telefono: str | None = None