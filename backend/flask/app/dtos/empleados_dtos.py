from dataclasses import dataclass

@dataclass(frozen=True)
class EmpleadoDTO_Output:
    id: int
    primer_nombre: str
    apellido: str
    ci: str
    telefono: str
    email: str
    segundo_nombre: str | None = None
    nombre_completo: str = ""

@dataclass(frozen=True)
class EmpleadoDTO_Input:
    primer_nombre: str
    apellido: str
    ci: str
    telefono: str
    email: str
    segundo_nombre: str | None = None
