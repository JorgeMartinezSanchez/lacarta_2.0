from sqlalchemy import select

from ..models import Empleado
from .repository import Repository


class EmpleadoRepository(Repository):
    model = Empleado
    default_order = (Empleado.id,)