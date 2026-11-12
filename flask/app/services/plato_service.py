from decimal import Decimal, InvalidOperation

from ..dtos.platos_dtos import PlatosDTO_Input, PlatosDTO_Output
from ..errors import BusinessRuleError, NotFoundError
from ..models import Plato
from ..repositories.plato_repository import PlatoRepository
from ..repositories.restaurantes_repository import RestauranteRepository


class PlatosService:
    def __init__(self, platos_repo: PlatoRepository, restaurantes_repo: RestauranteRepository):
        self.platos_repo = platos_repo
        self.restaurantes_repo = restaurantes_repo  # para validar que el restaurante exista

    # --- lectura ---------------------------------------------------------

    def get_all_platos(self) -> list[PlatosDTO_Output]:
        try:
            platos = self.platos_repo.getAll()
            return [self._to_dto(p) for p in platos]
        finally:
            self.platos_repo.close()

    def get_plato(self, plato_id: int) -> PlatosDTO_Output:
        try:
            return self._to_dto(self._find(plato_id))
        finally:
            self.platos_repo.close()

    # --- escritura -------------------------------------------------------

    def create_plato(self, newPlato: PlatosDTO_Input) -> PlatosDTO_Output:
        try:
            datos = self._normalizar_y_validar(newPlato)

            plato = self.platos_repo.create(Plato(**datos))
            self.platos_repo.commit()

            return self._to_dto(plato)
        except Exception:
            self.platos_repo.rollback()
            raise
        finally:
            self.platos_repo.close()

    def update_plato(self, plato_id: int, platoData: PlatosDTO_Input) -> PlatosDTO_Output:
        try:
            plato = self._find(plato_id)
            datos = self._normalizar_y_validar(platoData)

            plato = self.platos_repo.update(plato, **datos)
            self.platos_repo.commit()

            return self._to_dto(plato)
        except Exception:
            self.platos_repo.rollback()
            raise
        finally:
            self.platos_repo.close()

    def delete_plato(self, plato_id: int) -> None:
        try:
            plato = self._find(plato_id)
            # Si el plato está en algún pedido, la FK de item_pedido impide borrarlo:
            # el IntegrityError sube después del rollback.
            self.platos_repo.delete(plato)
            self.platos_repo.commit()
        except Exception:
            self.platos_repo.rollback()
            raise
        finally:
            self.platos_repo.close()

    # --- ayudantes privados ----------------------------------------------

    def _find(self, plato_id: int) -> Plato:
        plato = self.platos_repo.getOne(plato_id)
        if plato is None:
            raise NotFoundError(f"No existe el plato {plato_id}.")
        return plato

    def _normalizar_y_validar(self, dto: PlatosDTO_Input) -> dict:
        nombre = (dto.nombre or "").strip()
        if not nombre:
            raise BusinessRuleError("El nombre del plato es obligatorio.")

        try:
            precio = Decimal(str(dto.precio))
        except (InvalidOperation, TypeError, ValueError):
            raise BusinessRuleError("El precio no es un número válido.") from None
        if precio <= 0:
            raise BusinessRuleError("El precio debe ser mayor a 0.")

        if self.restaurantes_repo.getOne(dto.restaurante_id) is None:
            raise BusinessRuleError("Debes elegir un restaurante válido.")

        return {
            "nombre": nombre,
            "precio": precio,
            "disponible": bool(dto.disponible),
            "restaurante_id": dto.restaurante_id,
        }

    @staticmethod
    def _to_dto(p: Plato) -> PlatosDTO_Output:
        return PlatosDTO_Output(
            id=p.id,
            restaurante_id=p.restaurante_id,
            nombre=p.nombre,
            precio=float(p.precio),
            disponible=bool(p.disponible),
        )
