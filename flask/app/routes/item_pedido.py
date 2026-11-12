"""Controlador de ítems de pedido (capa de presentación)."""
from flask import Blueprint, abort, flash, redirect, request, url_for

from ..auth import requires_auth
from ..dtos.item_pedido_dtos import ItemPedidosDTO_Input
from ..errors import BusinessRuleError, NotFoundError
from .dependencias import items_service

bp = Blueprint("items_pedido", __name__, url_prefix="/items")


@bp.post("/pedido/<int:pedido_id>")
@requires_auth("write:pedidos")
def agregar_item(payload, pedido_id):
    try:
        items_service().create_item(ItemPedidosDTO_Input(
            pedido_id=pedido_id,
            plato_id=request.form.get("plato_id", type=int),
            cantidad=request.form.get("cantidad", ""),  # el servicio la valida
        ))
        flash("Item agregado.", "success")
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
    return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido_id))


@bp.post("/<int:item_id>/eliminar")
@requires_auth("delete:pedidos")
def eliminar_item(payload, item_id):
    service = items_service()
    try:
        pedido_id = service.get_item(item_id).pedido_id
        service.delete_item(item_id)
        flash("Item eliminado.", "success")
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
    return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido_id))
