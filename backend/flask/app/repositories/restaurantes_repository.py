from ..models import Restaurante
from .repository import Repository


class RestauranteRepository(Repository):
    model = Restaurante
    default_order = (Restaurante.nombre,)

    # getAll, getOne, create, update, delete, commit y rollback se heredan.
    # Aquí solo van las consultas propias de Restaurante.

    def listar_por_ciudad(self, ciudad):
        return self._listar(Restaurante.ciudad.ilike(f"%{ciudad}%"))
