"""Controlador de restaurantes (capa de presentación).

Solo hace tres cosas: leer la petición, llamar al servicio y responder
(render_template / redirect / flash). No toca db ni modelos.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..auth import requires_auth
from ..dtos.restaurantes_dtos import RestauranteDTO_Input
from ..errors import BusinessRuleError, NotFoundError
from .dependencias import platos_service, restaurantes_service

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
