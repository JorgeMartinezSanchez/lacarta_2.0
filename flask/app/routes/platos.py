from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from ..models import db, Plato, Restaurante
from ..auth import requires_auth

bp = Blueprint("platos", __name__, url_prefix="/platos")


# Listar todos los platos (con filtro opcional por restaurante)
@bp.get("/")
def listar_platos():
    restaurante_id = request.args.get("restaurante_id", type=int)
    consulta = Plato.query.order_by(Plato.nombre)
    if restaurante_id:
        consulta = consulta.filter(Plato.restaurante_id == restaurante_id)
    return render_template("platos/index.html", platos=consulta.all())


@bp.get("/<int:plato_id>")
def detalle_plato(plato_id):
    plato = db.get_or_404(Plato, plato_id)
    return render_template("platos/detalle.html", plato=plato)


# Crear plato DENTRO de un restaurante (necesita restaurante_id en la URL)
@bp.post("/restaurante/<int:restaurante_id>")
@requires_auth("write:carta")
def agregar_plato(payload, restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)

    nombre = request.form.get("nombre", "").strip()
    try:
        precio = Decimal(request.form.get("precio", ""))
    except InvalidOperation:
        precio = None

    if not nombre or precio is None or precio <= 0:
        flash("El plato necesita nombre y un precio mayor a 0.", "error")
        return redirect(url_for("restaurantes.detalle_restaurante",
                                restaurante_id=restaurante.id))

    db.session.add(Plato(
        nombre=nombre,
        precio=precio,
        disponible="disponible" in request.form,
        restaurante_id=restaurante.id,
    ))
    db.session.commit()
    flash("Plato agregado.", "success")
    return redirect(url_for("restaurantes.detalle_restaurante",
                            restaurante_id=restaurante.id))


@bp.route("/<int:plato_id>/editar", methods=["GET", "POST"])
@requires_auth("write:carta")
def editar_plato(payload, plato_id):
    plato = db.get_or_404(Plato, plato_id)
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        try:
            precio = Decimal(request.form.get("precio", ""))
        except InvalidOperation:
            precio = None
        if not nombre or precio is None or precio <= 0:
            flash("El plato necesita nombre y un precio mayor a 0.", "error")
            return render_template("platos/formulario.html", plato=plato), 400
        plato.nombre = nombre
        plato.precio = precio
        plato.disponible = "disponible" in request.form
        db.session.commit()
        flash("Plato actualizado.", "success")
        return redirect(url_for("platos.detalle_plato", plato_id=plato.id))
    return render_template("platos/formulario.html", plato=plato)


@bp.post("/<int:plato_id>/eliminar")
@requires_auth("delete:carta")
def eliminar_plato(payload, plato_id):
    plato = db.get_or_404(Plato, plato_id)
    try:
        db.session.delete(plato)
        db.session.commit()
        flash("Plato eliminado.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se puede eliminar: está en un pedido.", "error")
        return redirect(url_for("platos.detalle_plato", plato_id=plato_id))
    return redirect(url_for("platos.listar_platos"))