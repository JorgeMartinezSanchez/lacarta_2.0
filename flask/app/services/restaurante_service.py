import logging
from ..dtos.restaurantes_dtos import RestauranteDTO_Input, RestauranteDTO_Output
from ..errors import BusinessRuleError, NotFoundError
from ..models import Restaurante
from ..repositories.restaurantes_repository import RestauranteRepository

logger = logging.getLogger(__name__)


class RestaurantesService:
    def __init__(self, restaurantes_repo: RestauranteRepository):
        self.restaurantes_repo = restaurantes_repo


    def get_all_restaurants(self, ciudad: str | None = None) -> list[RestauranteDTO_Output]:
        try:
            ciudad = (ciudad or "").strip()
            if ciudad:
                restaurantes = self.restaurantes_repo.listar_por_ciudad(ciudad)
            else:
                restaurantes = self.restaurantes_repo.getAll()
            return [self._to_dto(r) for r in restaurantes]
        finally:
            self.restaurantes_repo.close()

    def get_restaurant(self, res_id: int) -> RestauranteDTO_Output:
        try:
            return self._to_dto(self._find(res_id))
        finally:
            self.restaurantes_repo.close()


    def create_restaurant(self, newRes: RestauranteDTO_Input) -> RestauranteDTO_Output:
        try:
            # 1. Normalizar y 2. validar reglas de negocio
            datos = self._normalizar_y_validar(newRes)

            # 3. Persistir (el servicio es dueño de la transacción)
            restaurante = self.restaurantes_repo.create(Restaurante(**datos))
            self.restaurantes_repo.commit()

            # 4. Devolver un DTO
            return self._to_dto(restaurante)
        except BusinessRuleError as e:
            # Error esperado (validación / regla de negocio): lo ve el usuario.
            self.restaurantes_repo.rollback()
            logger.warning("create_restaurant(newRes=%r) rechazado: %s", newRes, e)
            raise
        except Exception:
            # Error inesperado (base de datos, bug): traza completa en el log.
            self.restaurantes_repo.rollback()
            logger.exception("create_restaurant(newRes=%r) falló", newRes)
            raise
        finally:
            self.restaurantes_repo.close()

    def update_restaurant(self, res_id: int, resData: RestauranteDTO_Input) -> RestauranteDTO_Output:
        try:
            restaurante = self._find(res_id)
            datos = self._normalizar_y_validar(resData)

            restaurante = self.restaurantes_repo.update(restaurante, **datos)
            self.restaurantes_repo.commit()

            return self._to_dto(restaurante)
        except BusinessRuleError as e:
            # Error esperado (validación / regla de negocio): lo ve el usuario.
            self.restaurantes_repo.rollback()
            logger.warning("update_restaurant(res_id=%r, resData=%r) rechazado: %s", res_id, resData, e)
            raise
        except Exception:

            self.restaurantes_repo.rollback()
            logger.exception("update_restaurant(res_id=%r, resData=%r) falló", res_id, resData)
            raise
        finally:
            self.restaurantes_repo.close()

    def delete_restaurant(self, res_id: int) -> None:
        try:
            restaurante = self._find(res_id)

            self.restaurantes_repo.delete(restaurante)
            self.restaurantes_repo.commit()
        except BusinessRuleError as e:

            self.restaurantes_repo.rollback()
            logger.warning("delete_restaurant(res_id=%r) rechazado: %s", res_id, e)
            raise
        except Exception:

            self.restaurantes_repo.rollback()
            logger.exception("delete_restaurant(res_id=%r) falló", res_id)
            raise
        finally:
            self.restaurantes_repo.close()


    def _find(self, res_id: int) -> Restaurante:
        restaurante = self.restaurantes_repo.getOne(res_id)
        if restaurante is None:
            raise NotFoundError(f"No existe el restaurante {res_id}.")
        return restaurante

    @staticmethod
    def _normalizar_y_validar(dto: RestauranteDTO_Input) -> dict:
        nombre = (dto.nombre or "").strip()
        ciudad = (dto.ciudad or "").strip()
        if not nombre:
            raise BusinessRuleError("El nombre del restaurante es obligatorio.")
        if not ciudad:
            raise BusinessRuleError("La ciudad es obligatoria.")
        return {
            "nombre": nombre,
            "ciudad": ciudad,
            "direccion": (dto.direccion or "").strip() or None,
            "telefono": (dto.telefono or "").strip() or None,
        }

    @staticmethod
    def _to_dto(r: Restaurante) -> RestauranteDTO_Output:
        return RestauranteDTO_Output(
            id=r.id,
            nombre=r.nombre,
            ciudad=r.ciudad,
            direccion=r.direccion,
            telefono=r.telefono,
            num_platos=len(r.platos),
        )
