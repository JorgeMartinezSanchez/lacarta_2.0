"""Controlador de platos (capa de presentación). Responde JSON."""
from flask import Blueprint, jsonify, request

from ..auth import requires_auth
from ..dtos.platos_dtos import PlatosDTO_Input
from .dependencias import platos_service
from .peticion import booleano, cuerpo_json, entero, texto

bp = Blueprint("platos", __name__, url_prefix="/platos")


def _dto_desde_json(restaurante_id: int | None = None) -> PlatosDTO_Input:
    data = cuerpo_json()
    return PlatosDTO_Input(
        restaurante_id=restaurante_id if restaurante_id is not None else entero(data, "restaurante_id"),
        nombre=texto(data, "nombre"),
        precio=data.get("precio"),  # el servicio lo valida y convierte
        disponible=booleano(data, "disponible", default=True),
    )


# Listar todos los platos (con filtro opcional ?restaurante_id=)
@bp.get("/")
def listar_platos():
    platos = platos_service().get_all_platos(
        restaurante_id=request.args.get("restaurante_id", type=int)
    )
    return jsonify(platos)


@bp.get("/<int:plato_id>")
def detalle_plato(plato_id):
    return jsonify(platos_service().get_plato(plato_id))


# Crear plato: el restaurante va en el cuerpo ({"restaurante_id": 1, ...})
@bp.post("/")
@requires_auth("write:carta")
def agregar_plato(payload):
    plato = platos_service().create_plato(_dto_desde_json())
    return jsonify(plato), 201


@bp.put("/<int:plato_id>")
@requires_auth("write:carta")
def editar_plato(payload, plato_id):
    service = platos_service()
    plato = service.get_plato(plato_id)
    # No se permite cambiar de restaurante: se conserva el actual.
    plato = service.update_plato(plato_id, _dto_desde_json(plato.restaurante_id))
    return jsonify(plato)


@bp.delete("/<int:plato_id>")
@requires_auth("delete:carta")
def eliminar_plato(payload, plato_id):
    platos_service().delete_plato(plato_id)
    return jsonify(mensaje="Plato eliminado.")
