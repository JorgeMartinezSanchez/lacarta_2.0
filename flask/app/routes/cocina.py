"""Controlador de la COCINA (capa de presentación).

- Ver la cola: read:pedidos (cocina y admin).
- Avanzar el estado: update:pedidos (solo cocina).
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..auth import requires_auth
from ..errors import BusinessRuleError, NotFoundError
from ..state.pedidos import OPCIONES as ESTADOS_PEDIDO, SIGUIENTE
from .dependencias import pedidos_service

bp = Blueprint("cocina", __name__, url_prefix="/cocina")


@bp.get("/")
@requires_auth("read:pedidos")
def cola(payload):
    pedidos = pedidos_service().get_cola_cocina()
    return render_template("cocina/index.html", pedidos=pedidos,
                           etiquetas=dict(ESTADOS_PEDIDO), siguiente=SIGUIENTE)


@bp.post("/<int:pedido_id>/avanzar")
@requires_auth("update:pedidos")
def avanzar(payload, pedido_id):
    nuevo_estado = request.form.get("estado", "")
    try:
        pedido = pedidos_service().avanzar(pedido_id, nuevo_estado)
        flash(f"Pedido #{pedido.id}: {dict(ESTADOS_PEDIDO)[pedido.estado]}.", "success")
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:   # transición inválida (p. ej. listo -> pendiente)
        flash(str(e), "error")
    return redirect(url_for("cocina.cola"))  # Post/Redirect/Get
