"""Controlador de pedidos (capa de presentación)."""
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..auth import requires_auth
from ..dtos.pedidos_dtos import PedidosDTO_Input
from ..errors import BusinessRuleError, NotFoundError
from ..state.pedidos import OPCIONES as ESTADOS_PEDIDO
from .dependencias import items_service, pedidos_service, platos_service, restaurantes_service

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@bp.get("/")
@requires_auth("read:pedidos")
def listar_pedidos(payload):
    pedidos = pedidos_service().get_all_pedidos(estado=request.args.get("estado"))
    return render_template("pedidos/index.html", pedidos=pedidos,
                           estados=ESTADOS_PEDIDO, etiquetas=dict(ESTADOS_PEDIDO))


@bp.get("/<int:pedido_id>")
@requires_auth("read:pedidos")
def detalle_pedido(payload, pedido_id):
    try:
        pedido = pedidos_service().get_pedido(pedido_id)
    except NotFoundError:
        abort(404)
    items = items_service().get_all_items(pedido_id=pedido_id)
    platos = platos_service().get_all_platos(restaurante_id=pedido.restaurante_id)
    return render_template("pedidos/detalle.html", pedido=pedido, items=items, platos=platos,
                           estados=ESTADOS_PEDIDO, etiquetas=dict(ESTADOS_PEDIDO))


@bp.route("/nuevo", methods=["GET", "POST"])
@requires_auth("create:pedidos")
def crear_pedido(payload):
    if request.method == "POST":
        try:
            pedido = pedidos_service().create_pedido(PedidosDTO_Input(
                restaurante_id=request.form.get("restaurante_id", type=int),
                estado="pendiente",   # el servicio lo fija igual: todo pedido nace pendiente
                fecha=date.today(),   # idem: la fecha la decide el servidor
                total=0,
            ), cliente=payload["sub"])   # R1.2: el cliente sale del token, no del formulario
        except BusinessRuleError as e:
            flash(str(e), "error")
            return render_template("pedidos/formulario.html",
                                   pedido=None,
                                   restaurantes=restaurantes_service().get_all_restaurants()), 400
        flash("Pedido creado.", "success")
        return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))

    # GET: permitir preseleccionar restaurante vía ?restaurante_id=
    return render_template("pedidos/formulario.html",
                           pedido=None,
                           restaurante_preseleccionado=request.args.get("restaurante_id", type=int),
                           restaurantes=restaurantes_service().get_all_restaurants())


@bp.post("/<int:pedido_id>/estado")
@requires_auth("write:pedidos")
def actualizar_estado(payload, pedido_id):
    try:
        pedidos_service().cambiar_estado(pedido_id, request.form.get("estado", ""))
        flash("Estado actualizado.", "success")
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:   # incluye TransicionInvalida del patrón State
        flash(str(e), "error")
    return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido_id))


@bp.post("/<int:pedido_id>/eliminar")
@requires_auth("delete:pedidos")
def eliminar_pedido(payload, pedido_id):
    try:
        pedidos_service().delete_pedido(pedido_id)
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
        return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido_id))
    flash("Pedido eliminado.", "success")
    return redirect(url_for("pedidos.listar_pedidos"))
