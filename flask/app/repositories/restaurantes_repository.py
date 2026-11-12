from ..models import Restaurante
from .repository import Repository


class RestauranteRepository(Repository):
    model = Restaurante
    default_order = (Restaurante.nombre,)

    # Aquí solo van las consultas propias de Restaurante.
    # getAll, getOne, create, update, delete, commit y rollback se heredan.
