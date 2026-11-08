from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from ..models import db, Restaurante
from ..auth import requires_auth

bp = Blueprint("restaurantes", __name__, url_prefix="/restaurantes")


@bp.get("/")
def listar_restaurantes():
    ciudad = request.args.get("ciudad", "").strip()
    consulta = Restaurante.query.order_by(Restaurante.nombre)
    if ciudad:
        consulta = consulta.filter(Restaurante.ciudad.ilike(f"%{ciudad}%"))
    return render_template("restaurantes/index.html", restaurantes=consulta.all())


@bp.get("/<int:restaurante_id>")
def detalle_restaurante(restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)
    return render_template("restaurantes/detalle.html", restaurante=restaurante)


@bp.route("/nuevo", methods=["GET", "POST"])
@requires_auth("write:carta")
def crear_restaurante(payload):
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        ciudad = request.form.get("ciudad", "").strip()
        if not nombre or not ciudad:
            flash("Nombre y ciudad son obligatorios.", "error")
            return render_template("restaurantes/formulario.html", restaurante=None), 400

        restaurante = Restaurante(
            nombre=nombre,
            ciudad=ciudad,
            direccion=request.form.get("direccion", "").strip() or None,
            telefono=request.form.get("telefono", "").strip() or None,
        )
        db.session.add(restaurante)
        db.session.commit()
        flash("Restaurante creado.", "success")
        return redirect(url_for("restaurantes.detalle_restaurante",
                                restaurante_id=restaurante.id))

    return render_template("restaurantes/formulario.html", restaurante=None)


@bp.route("/<int:restaurante_id>/editar", methods=["GET", "POST"])
@requires_auth("write:carta")
def editar_restaurante(payload, restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        ciudad = request.form.get("ciudad", "").strip()
        if not nombre or not ciudad:
            flash("Nombre y ciudad son obligatorios.", "error")
            return render_template("restaurantes/formulario.html",
                                   restaurante=restaurante), 400
        restaurante.nombre = nombre
        restaurante.ciudad = ciudad
        restaurante.direccion = request.form.get("direccion", "").strip() or None
        restaurante.telefono = request.form.get("telefono", "").strip() or None
        db.session.commit()
        flash("Restaurante actualizado.", "success")
        return redirect(url_for("restaurantes.detalle_restaurante",
                                restaurante_id=restaurante.id))
    return render_template("restaurantes/formulario.html", restaurante=restaurante)


@bp.post("/<int:restaurante_id>/eliminar")
@requires_auth("delete:carta")
def eliminar_restaurante(payload, restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)
    try:
        db.session.delete(restaurante)
        db.session.commit()
        flash("Restaurante eliminado.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se puede eliminar: tiene pedidos asociados.", "error")
        return redirect(url_for("restaurantes.detalle_restaurante",
                                restaurante_id=restaurante_id))
    return redirect(url_for("restaurantes.listar_restaurantes"))