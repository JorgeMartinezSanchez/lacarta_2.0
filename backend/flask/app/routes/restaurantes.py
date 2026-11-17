"""Controlador de restaurantes (capa de presentación).

Solo hace tres cosas: leer la petición, llamar al servicio y responder JSON.
No toca db ni modelos. Los errores (NotFoundError -> 404, BusinessRuleError -> 400)
los convierte en JSON register_error_handlers.
"""
from dataclasses import asdict

from flask import Blueprint, jsonify, request

from ..auth import requires_auth
from ..dtos.restaurantes_dtos import RestauranteDTO_Input
from .dependencias import platos_service, restaurantes_service
from .peticion import cuerpo_json, texto

bp = Blueprint("restaurantes", __name__, url_prefix="/restaurantes")


def _dto_desde_json() -> RestauranteDTO_Input:
    data = cuerpo_json()
    return RestauranteDTO_Input(
        nombre=texto(data, "nombre"),
        ciudad=texto(data, "ciudad"),
        direccion=texto(data, "direccion", None),
        telefono=texto(data, "telefono", None),
    )


@bp.get("/")
def listar_restaurantes():
    restaurantes = restaurantes_service().get_all_restaurants(ciudad=request.args.get("ciudad"))
    return jsonify(restaurantes)


@bp.get("/<int:restaurante_id>")
def detalle_restaurante(restaurante_id):
    restaurante = restaurantes_service().get_restaurant(restaurante_id)
    platos = platos_service().get_all_platos(restaurante_id=restaurante_id)
    return jsonify({**asdict(restaurante), "platos": platos})


@bp.post("/")
@requires_auth("write:carta")
def crear_restaurante(payload):
    restaurante = restaurantes_service().create_restaurant(_dto_desde_json())
    return jsonify(restaurante), 201


@bp.put("/<int:restaurante_id>")
@requires_auth("write:carta")
def editar_restaurante(payload, restaurante_id):
    restaurante = restaurantes_service().update_restaurant(restaurante_id, _dto_desde_json())
    return jsonify(restaurante)


@bp.delete("/<int:restaurante_id>")
@requires_auth("delete:carta")
def eliminar_restaurante(payload, restaurante_id):
    restaurantes_service().delete_restaurant(restaurante_id)
    return jsonify(mensaje="Restaurante eliminado.")
