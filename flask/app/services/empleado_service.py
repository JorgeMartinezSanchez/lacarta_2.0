import logging

from ..dtos.empleados_dtos import EmpleadoDTO_Input, EmpleadoDTO_Output
from ..errors import BusinessRuleError, NotFoundError
from ..models import Empleado
from ..repositories.empleado_repository import EmpleadoRepository

logger = logging.getLogger(__name__)


class EmpleadoService:
    def __init__(self, empleado_repo: EmpleadoRepository):
        self.empleado_repo = empleado_repo


    def get_all_empleados(self) -> list[EmpleadoDTO_Output]:
        try:
            return [self._to_dto(e) for e in self.empleado_repo.getAll()]
        finally:
            self.empleado_repo.close()

    def get_empleado(self, emp_id: int) -> EmpleadoDTO_Output:
        try:
            return self._to_dto(self._find(emp_id))
        finally:
            self.empleado_repo.close()


    def create_empleado(self, newEmp: EmpleadoDTO_Input) -> EmpleadoDTO_Output:
        try:
            datos = self._normalizar_y_validar(newEmp)

            empleado = self.empleado_repo.create(Empleado(**datos))
            self.empleado_repo.commit()

            return self._to_dto(empleado)
        except BusinessRuleError as e:
            self.empleado_repo.rollback()
            logger.warning("create_empleado(newEmp=%r) rechazado: %s", newEmp, e)
            raise
        except Exception:
            self.empleado_repo.rollback()
            logger.exception("create_empleado(newEmp=%r) falló", newEmp)
            raise
        finally:
            self.empleado_repo.close()

    def update_empleado(self, emp_id: int, empData: EmpleadoDTO_Input) -> EmpleadoDTO_Output:
        try:
            empleado = self._find(emp_id)
            datos = self._normalizar_y_validar(empData)

            empleado = self.empleado_repo.update(empleado, **datos)
            self.empleado_repo.commit()

            return self._to_dto(empleado)
        except BusinessRuleError as e:
            self.empleado_repo.rollback()
            logger.warning("update_empleado(emp_id=%r, empData=%r) rechazado: %s", emp_id, empData, e)
            raise
        except Exception:
            self.empleado_repo.rollback()
            logger.exception("update_empleado(emp_id=%r, empData=%r) falló", emp_id, empData)
            raise
        finally:
            self.empleado_repo.close()

    def delete_empleado(self, emp_id: int) -> None:
        try:
            empleado = self._find(emp_id)

            self.empleado_repo.delete(empleado)
            self.empleado_repo.commit()
        except BusinessRuleError as e:
            self.empleado_repo.rollback()
            logger.warning("delete_empleado(emp_id=%r) rechazado: %s", emp_id, e)
            raise
        except Exception:
            self.empleado_repo.rollback()
            logger.exception("delete_empleado(emp_id=%r) falló", emp_id)
            raise
        finally:
            self.empleado_repo.close()


    def _find(self, emp_id: int) -> Empleado:
        empleado = self.empleado_repo.getOne(emp_id)
        if empleado is None:
            raise NotFoundError(f"No existe el empleado {emp_id}.")
        return empleado

    @staticmethod
    def _normalizar_y_validar(dto: EmpleadoDTO_Input) -> dict:
        datos = {
            "primer_nombre": (dto.primer_nombre or "").strip(),
            "apellido": (dto.apellido or "").strip(),
            "ci": (dto.ci or "").strip(),
            "telefono": (dto.telefono or "").strip(),
            "email": (dto.email or "").strip().lower(),
        }
        obligatorios = {
            "primer_nombre": "El primer nombre es obligatorio.",
            "apellido": "El apellido es obligatorio.",
            "ci": "El CI es obligatorio.",
            "telefono": "El teléfono es obligatorio.",
            "email": "El email es obligatorio.",
        }
        for campo, mensaje in obligatorios.items():
            if not datos[campo]:
                raise BusinessRuleError(mensaje)
        if "@" not in datos["email"]:
            raise BusinessRuleError("El email no es válido.")

        datos["segundo_nombre"] = (dto.segundo_nombre or "").strip() or None
        return datos

    @staticmethod
    def _to_dto(e: Empleado) -> EmpleadoDTO_Output:
        partes = [e.primer_nombre, e.segundo_nombre, e.apellido]
        return EmpleadoDTO_Output(
            id=e.id,
            primer_nombre=e.primer_nombre,
            segundo_nombre=e.segundo_nombre,
            apellido=e.apellido,
            ci=e.ci,
            telefono=e.telefono,
            email=e.email,
            nombre_completo=" ".join(p for p in partes if p),
        )
