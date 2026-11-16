"""Controlador de restaurantes (capa de presentación).

Solo hace tres cosas: leer la petición, llamar al servicio y responder
(render_template / redirect / flash). No toca db ni modelos.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..auth import requires_auth
from ..dtos.pedidos_dtos import ItemNuevoDTO, NuevoPedidoDTO
from ..dtos.restaurantes_dtos import RestauranteDTO_Input
from ..errors import BusinessRuleError, NotFoundError
from .dependencias import pedidos_service, platos_service, restaurantes_service

bp = Blueprint("restaurantes", __name__, url_prefix="/restaurantes")


def _dto_desde_form() -> RestauranteDTO_Input:
    return RestauranteDTO_Input(
        nombre=request.form.get("nombre", ""),
        ciudad=request.form.get("ciudad", ""),
        direccion=request.form.get("direccion"),
        telefono=request.form.get("telefono"),
    )


@bp.get("/")
def listar_restaurantes():
    restaurantes = restaurantes_service().get_all_restaurants(ciudad=request.args.get("ciudad"))
    return render_template("restaurantes/index.html", restaurantes=restaurantes)


@bp.get("/<int:restaurante_id>")
def detalle_restaurante(restaurante_id):
    try:
        restaurante = restaurantes_service().get_restaurant(restaurante_id)
    except NotFoundError:
        abort(404)
    platos = platos_service().get_all_platos(restaurante_id=restaurante_id)
    return render_template("restaurantes/detalle.html", restaurante=restaurante, platos=platos)


@bp.route("/nuevo", methods=["GET", "POST"])
@requires_auth("write:carta")
def crear_restaurante(payload):
    if request.method == "POST":
        try:
            restaurante = restaurantes_service().create_restaurant(_dto_desde_form())
        except BusinessRuleError as e:
            flash(str(e), "error")
            return render_template("restaurantes/formulario.html", restaurante=None), 400
        flash("Restaurante creado.", "success")
        return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante.id))

    return render_template("restaurantes/formulario.html", restaurante=None)


@bp.route("/<int:restaurante_id>/editar", methods=["GET", "POST"])
@requires_auth("write:carta")
def editar_restaurante(payload, restaurante_id):
    service = restaurantes_service()
    try:
        if request.method == "POST":
            service.update_restaurant(restaurante_id, _dto_desde_form())
            flash("Restaurante actualizado.", "success")
            return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante_id))
        restaurante = service.get_restaurant(restaurante_id)
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
        restaurante = service.get_restaurant(restaurante_id)
        return render_template("restaurantes/formulario.html", restaurante=restaurante), 400
    return render_template("restaurantes/formulario.html", restaurante=restaurante)


@bp.post("/<int:restaurante_id>/eliminar")
@requires_auth("delete:carta")
def eliminar_restaurante(payload, restaurante_id):
    try:
        restaurantes_service().delete_restaurant(restaurante_id)
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
        return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante_id))
    flash("Restaurante eliminado.", "success")
    return redirect(url_for("restaurantes.listar_restaurantes"))


# --- R1: hacer un pedido (cliente) ------------------------------------------

def _items_desde_form() -> tuple[ItemNuevoDTO, ...]:
    """Lee los campos cantidad_<plato_id> del formulario.

    Solo platos y cantidades (R1.4): si alguien agrega un campo "precio" o "total"
    con las herramientas del navegador, aquí simplemente no se lee.
    Las cantidades vacías o 0 significan "no pido este plato".
    """
    items = []
    for campo, valor in request.form.items():
        if not campo.startswith("cantidad_"):
            continue
        valor = valor.strip()
        if valor in ("", "0"):
            continue
        try:
            plato_id = int(campo.removeprefix("cantidad_"))
        except ValueError:
            raise BusinessRuleError("El formulario trae un plato inválido.") from None
        items.append(ItemNuevoDTO(plato_id=plato_id, cantidad=valor))
    return tuple(items)


@bp.route("/<int:restaurante_id>/pedir", methods=["GET", "POST"])
@requires_auth("create:pedidos")
def pedir(payload, restaurante_id):
    try:
        restaurante = restaurantes_service().get_restaurant(restaurante_id)
    except NotFoundError:
        abort(404)

    if request.method == "POST":
        try:
            pedido = pedidos_service().create_pedido(
                NuevoPedidoDTO(restaurante_id=restaurante_id, items=_items_desde_form()),
                cliente=payload["sub"],   # R1.2: el cliente sale del token, no del formulario
            )
        except NotFoundError:
            abort(404)
        except BusinessRuleError as e:
            flash(str(e), "error")
            platos = platos_service().get_all_platos(restaurante_id=restaurante_id)
            return render_template("pedidos/formulario.html", restaurante=restaurante,
                                   platos=platos, cantidades=request.form), 400
        flash(f"Pedido #{pedido.id} creado. Total: ${pedido.total:.2f}", "success")
        return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))  # Post/Redirect/Get

    platos = platos_service().get_all_platos(restaurante_id=restaurante_id)
    return render_template("pedidos/formulario.html", restaurante=restaurante,
                           platos=platos, cantidades={})
