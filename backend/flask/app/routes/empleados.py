"""Controlador de empleados (capa de presentación).

Solo hace tres cosas: leer la petición, llamar al servicio y responder JSON.
No toca db ni modelos.
Todas las rutas son privadas: los empleados tienen datos personales (CI, teléfono).
"""
from flask import Blueprint, jsonify

from ..auth import requires_auth
from ..dtos.empleados_dtos import EmpleadoDTO_Input
from .dependencias import empleados_service
from .peticion import cuerpo_json, texto

bp = Blueprint("empleados", __name__, url_prefix="/empleados")


def _dto_desde_json() -> EmpleadoDTO_Input:
    data = cuerpo_json()
    return EmpleadoDTO_Input(
        primer_nombre=texto(data, "primer_nombre"),
        segundo_nombre=texto(data, "segundo_nombre", None),
        apellido=texto(data, "apellido"),
        ci=texto(data, "ci"),
        telefono=texto(data, "telefono"),
        email=texto(data, "email"),
    )


@bp.get("/")
@requires_auth("read:empleados")
def listar_empleados(payload):
    return jsonify(empleados_service().get_all_empleados())


@bp.get("/<int:empleado_id>")
@requires_auth("read:empleados")
def detalle_empleado(payload, empleado_id):
    return jsonify(empleados_service().get_empleado(empleado_id))


@bp.post("/")
@requires_auth("write:empleados")
def crear_empleado(payload):
    empleado = empleados_service().create_empleado(_dto_desde_json())
    return jsonify(empleado), 201


@bp.put("/<int:empleado_id>")
@requires_auth("write:empleados")
def editar_empleado(payload, empleado_id):
    return jsonify(empleados_service().update_empleado(empleado_id, _dto_desde_json()))


@bp.delete("/<int:empleado_id>")
@requires_auth("delete:empleados")
def eliminar_empleado(payload, empleado_id):
    empleados_service().delete_empleado(empleado_id)
    return jsonify(mensaje="Empleado eliminado.")
