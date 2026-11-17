"""Controlador de pedidos del CLIENTE (capa de presentación). Responde JSON.

Todas las rutas filtran por el 'sub' del token: un cliente nunca ve ni toca
pedidos ajenos (R2.6: el pedido de otro responde 404, no 403, para no
confirmar que existe).
"""
from flask import Blueprint, jsonify

from ..auth import requires_auth
from ..dtos.pedidos_dtos import ItemNuevoDTO, NuevoPedidoDTO
from ..errors import BusinessRuleError
from .dependencias import pedidos_service
from .peticion import cuerpo_json, entero

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


def _items_desde_json(data: dict) -> tuple[ItemNuevoDTO, ...]:
    """Lee items: [{"plato_id": 1, "cantidad": 2}, ...].

    Solo platos y cantidades (R1.4): si alguien agrega "precio_unitario" o
    "total" al JSON, aquí simplemente no se lee.
    """
    items = data.get("items")
    if not isinstance(items, list):
        raise BusinessRuleError("'items' debe ser una lista de {plato_id, cantidad}.")
    resultado = []
    for item in items:
        if not isinstance(item, dict):
            raise BusinessRuleError("Cada ítem debe ser un objeto {plato_id, cantidad}.")
        
        cantidad = item.get("cantidad")
        if isinstance(cantidad, (bool, float)):  # 1.5 no debe convertirse en 1
            raise BusinessRuleError("La cantidad debe ser un número entero.")
        
        resultado.append(ItemNuevoDTO(plato_id=entero(item, "plato_id"), cantidad=cantidad))
    return tuple(resultado)


@bp.get("/")
@requires_auth("read:mis-pedidos")
def listar_pedidos(payload):
    return jsonify(pedidos_service().get_mis_pedidos(cliente=payload["sub"]))


@bp.get("/<int:pedido_id>")
@requires_auth("read:mis-pedidos")
def detalle_pedido(payload, pedido_id):
    return jsonify(pedidos_service().get_mi_pedido(pedido_id, cliente=payload["sub"]))


# R1: hacer un pedido. Cuerpo: {"restaurante_id": 1, "items": [{"plato_id": 2, "cantidad": 1}]}
@bp.post("/")
@requires_auth("create:pedidos")
def crear_pedido(payload):
    data = cuerpo_json()
    pedido = pedidos_service().create_pedido(
        NuevoPedidoDTO(restaurante_id=entero(data, "restaurante_id"),
                       items=_items_desde_json(data)),
        cliente=payload["sub"],   # R1.2: el cliente sale del token, no del cuerpo
    )
    return jsonify(pedido), 201


@bp.post("/<int:pedido_id>/cancelar")
@requires_auth("read:mis-pedidos")
def cancelar_pedido(payload, pedido_id):
    # Si ya está en preparación, el patrón State lanza BusinessRuleError -> 400
    return jsonify(pedidos_service().cancelar(pedido_id, cliente=payload["sub"]))
