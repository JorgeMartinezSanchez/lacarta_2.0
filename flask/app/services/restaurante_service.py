from ..dtos.restaurantes_dtos import RestauranteDTO_Input, RestauranteDTO_Output
from ..errors import BusinessRuleError
from ..models import Restaurante
from ..repositories.restaurantes_repository import RestauranteRepository


class RestaurantesService:
    def __init__(self, restaurantes_repo: RestauranteRepository):
        self.restaurantes_repo = restaurantes_repo

    def create_restaurant(self, newRes: RestauranteDTO_Input) -> RestauranteDTO_Output:
        # 1. Normalizar: quitar espacios y convertir "" en None
        nombre = (newRes.nombre or "").strip()
        ciudad = (newRes.ciudad or "").strip()
        direccion = (newRes.direccion or "").strip() or None
        telefono = (newRes.telefono or "").strip() or None

        # 2. Reglas de negocio (fuera del try: aquí no hay nada que deshacer)
        if not nombre:
            raise BusinessRuleError("El nombre del restaurante es obligatorio.")
        if not ciudad:
            raise BusinessRuleError("La ciudad es obligatoria.")

        # 3. Persistir (el servicio es dueño de la transacción)
        try:
            restaurante = self.restaurantes_repo.create(Restaurante(
                nombre=nombre,
                ciudad=ciudad,
                direccion=direccion,
                telefono=telefono,
            ))
            self.restaurantes_repo.commit()
        except Exception:
            # Si falla el INSERT o el commit, la sesión queda inutilizable
            # hasta hacer rollback. Se deshace y se deja subir el error.
            self.restaurantes_repo.rollback()
            raise

        # 4. Devolver un DTO
        return RestauranteDTO_Output(
            id=restaurante.id,
            nombre=restaurante.nombre,
            ciudad=restaurante.ciudad,
            direccion=restaurante.direccion,
            telefono=restaurante.telefono,
        )
