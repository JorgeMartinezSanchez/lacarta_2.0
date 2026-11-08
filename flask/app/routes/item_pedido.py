from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, request, url_for
from sqlalchemy.exc import IntegrityError

from ..models import db, Pedido, Plato, ItemPedido
from ..auth import requires_auth

bp = Blueprint("items_pedido", __name__, url_prefix="/items")


@bp.post("/pedido/<int:pedido_id>")
@requires_auth("write:pedidos")
def agregar_item(payload, pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)

    plato_id = request.form.get("plato_id", type=int)
    plato = db.session.get(Plato, plato_id) if plato_id else None
    if plato is None or plato.restaurante_id != pedido.restaurante_id:
        flash("El plato no pertenece a este restaurante.", "error")
        return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))

    cantidad_raw = request.form.get("cantidad", "").strip()
    try:
        cantidad = Decimal(cantidad_raw)
    except InvalidOperation:
        cantidad = None
    if cantidad is None or cantidad <= 0:
        flash("Cantidad inválida.", "error")
        return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))

    item = ItemPedido(
        pedido_id=pedido.id,
        plato_id=plato.id,
        restaurante_id=pedido.restaurante_id,
        cantidad=str(cantidad),      # tu modelo lo define como String
        precio_unitario=plato.precio,
    )
    db.session.add(item)
    _recalcular_total(pedido)
    db.session.commit()
    flash("Item agregado.", "success")
    return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))


@bp.post("/<int:item_id>/eliminar")
@requires_auth("delete:pedidos")
def eliminar_item(payload, item_id):
    item = db.get_or_404(ItemPedido, item_id)
    pedido = item.pedido if hasattr(item, "pedido") else db.session.get(Pedido, item.pedido_id)
    db.session.delete(item)
    _recalcular_total(pedido)
    db.session.commit()
    flash("Item eliminado.", "success")
    return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))


def _recalcular_total(pedido: Pedido) -> None:
    """Recalcula pedido.total a partir de sus items."""
    db.session.flush()  # asegurar que los items nuevos ya estén en la sesión
    total = Decimal("0.00")
    for item in ItemPedido.query.filter_by(pedido_id=pedido.id).all():
        try:
            total += Decimal(item.cantidad) * item.precio_unitario
        except InvalidOperation:
            continue
    pedido.total = total