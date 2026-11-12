"""Controlador de platos (capa de presentación)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..auth import requires_auth
from ..dtos.platos_dtos import PlatosDTO_Input
from ..errors import BusinessRuleError, NotFoundError
from .dependencias import platos_service

bp = Blueprint("platos", __name__, url_prefix="/platos")


def _dto_desde_form(restaurante_id: int) -> PlatosDTO_Input:
    return PlatosDTO_Input(
        restaurante_id=restaurante_id,
        nombre=request.form.get("nombre", ""),
        precio=request.form.get("precio", ""),  # el servicio lo valida y convierte
        disponible="disponible" in request.form,
    )


# Listar todos los platos (con filtro opcional por restaurante)
@bp.get("/")
def listar_platos():
    platos = platos_service().get_all_platos(
        restaurante_id=request.args.get("restaurante_id", type=int)
    )
    return render_template("platos/index.html", platos=platos)


@bp.get("/<int:plato_id>")
def detalle_plato(plato_id):
    try:
        plato = platos_service().get_plato(plato_id)
    except NotFoundError:
        abort(404)
    return render_template("platos/detalle.html", plato=plato)


# Crear plato DENTRO de un restaurante (necesita restaurante_id en la URL)
@bp.post("/restaurante/<int:restaurante_id>")
@requires_auth("write:carta")
def agregar_plato(payload, restaurante_id):
    try:
        platos_service().create_plato(_dto_desde_form(restaurante_id))
        flash("Plato agregado.", "success")
    except BusinessRuleError as e:
        flash(str(e), "error")
    return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante_id))


@bp.route("/<int:plato_id>/editar", methods=["GET", "POST"])
@requires_auth("write:carta")
def editar_plato(payload, plato_id):
    service = platos_service()
    try:
        plato = service.get_plato(plato_id)
        if request.method == "POST":
            # El formulario no permite cambiar de restaurante: se conserva el actual.
            service.update_plato(plato_id, _dto_desde_form(plato.restaurante_id))
            flash("Plato actualizado.", "success")
            return redirect(url_for("platos.detalle_plato", plato_id=plato_id))
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
        return render_template("platos/formulario.html", plato=plato), 400
    return render_template("platos/formulario.html", plato=plato)


@bp.post("/<int:plato_id>/eliminar")
@requires_auth("delete:carta")
def eliminar_plato(payload, plato_id):
    try:
        platos_service().delete_plato(plato_id)
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
        return redirect(url_for("platos.detalle_plato", plato_id=plato_id))
    flash("Plato eliminado.", "success")
    return redirect(url_for("platos.listar_platos"))
