from ..models import Plato
from .repository import Repository


class PlatoRepository(Repository):
    model = Plato
    default_order = (Plato.nombre,)
