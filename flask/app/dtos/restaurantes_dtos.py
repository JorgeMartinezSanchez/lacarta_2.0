@dataclass(frozen=True)
class RestauranteDTO_Output:
    id: int
    nombre: str
    ciudad: str
    direccion: str
    telefono: str

@dataclass(frozen=True)
class RestauranteDTO_Input:
    nombre: str
    ciudad: str
    direccion: str
    telefono: str