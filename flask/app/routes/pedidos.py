"""Controlador de pedidos del CLIENTE (capa de presentación).

Todas las rutas usan read:mis-pedidos y filtran por el 'sub' del token:
un cliente nunca ve ni toca pedidos ajenos. Crear un pedido está en
restaurantes.pedir (/restaurantes/<id>/pedir).
"""
from flask import Blueprint, abort, flash, redirect, render_template, url_for

from ..auth import requires_auth
from ..errors import BusinessRuleError, NotFoundError
from ..state.pedidos import OPCIONES as ESTADOS_PEDIDO
from .dependencias import pedidos_service

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@bp.get("/")
@requires_auth("read:mis-pedidos")
def listar_pedidos(payload):
    pedidos = pedidos_service().get_mis_pedidos(cliente=payload["sub"])
    return render_template("pedidos/index.html", pedidos=pedidos, etiquetas=dict(ESTADOS_PEDIDO))


@bp.get("/<int:pedido_id>")
@requires_auth("read:mis-pedidos")
def detalle_pedido(payload, pedido_id):
    try:
        pedido = pedidos_service().get_mi_pedido(pedido_id, cliente=payload["sub"])
    except NotFoundError:
        abort(404)  # R2.6: 404 y no 403, para no confirmar que el pedido existe
    return render_template("pedidos/detalle.html", pedido=pedido, etiquetas=dict(ESTADOS_PEDIDO))


@bp.post("/<int:pedido_id>/cancelar")
@requires_auth("read:mis-pedidos")
def cancelar_pedido(payload, pedido_id):
    try:
        pedidos_service().cancelar(pedido_id, cliente=payload["sub"])
        flash("Pedido cancelado.", "success")
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:   # p. ej. ya está en preparación
        flash(str(e), "error")
    return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido_id))  # Post/Redirect/Get
