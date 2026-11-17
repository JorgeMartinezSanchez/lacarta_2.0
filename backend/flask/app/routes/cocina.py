"""Controlador de la COCINA (capa de presentación). Responde JSON.

- Ver la cola: read:pedidos (cocina y admin).
- Avanzar el estado: update:pedidos (solo cocina).
"""
from dataclasses import asdict

from flask import Blueprint, jsonify

from ..auth import requires_auth
from ..state.pedidos import SIGUIENTE
from .dependencias import pedidos_service
from .peticion import cuerpo_json, texto

bp = Blueprint("cocina", __name__, url_prefix="/cocina")


def _con_siguiente(pedido) -> dict:
    """Agrega el estado al que la cocina puede pasar el pedido (el botón "Pasar a ...")."""
    sig = SIGUIENTE.get(pedido.estado)
    return {**asdict(pedido),
            "siguiente": {"estado": sig.nombre, "etiqueta": sig.etiqueta} if sig else None}


@bp.get("/")
@requires_auth("read:pedidos")
def cola(payload):
    return jsonify([_con_siguiente(p) for p in pedidos_service().get_cola_cocina()])


# Cuerpo: {"estado": "en_preparacion"}. Una transición inválida responde 400.
@bp.post("/<int:pedido_id>/avanzar")
@requires_auth("update:pedidos")
def avanzar(payload, pedido_id):
    nuevo_estado = texto(cuerpo_json(), "estado")
    pedido = pedidos_service().avanzar(pedido_id, nuevo_estado)
    return jsonify(_con_siguiente(pedido))
