from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from ..models import db, Restaurante, Plato, Pedido, ItemPedido
from ..auth import requires_auth
from ..extensions import db

bp = Blueprint("restaurantes", __name__, url_prefix="/restaurantes")


# ---------- READ: listar (con filtro por ciudad) ----------
@bp.get("/")
def listar_restaurantes():
    ciudad = request.args.get("ciudad", "").strip()
    consulta = Restaurante.query.order_by(Restaurante.nombre)
    if ciudad:
        consulta = consulta.filter(Restaurante.ciudad.ilike(f"%{ciudad}%"))
    return render_template("restaurantes/index.html", restaurantes=consulta.all())


# ---------- READ: detalle ----------
@bp.get("/<int:restaurante_id>")
def detalle_restaurante(restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)
    return render_template("restaurantes/detalle.html", restaurante=restaurante)


# ---------- CREATE ----------
@bp.route("/nuevo", methods=["GET", "POST"])
def crear_restaurante():
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
        return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante.id))

    return render_template("restaurantes/formulario.html", restaurante=None)


# ---------- UPDATE ----------
@bp.route("/<int:restaurante_id>/editar", methods=["GET", "POST"])
def editar_restaurante(restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        ciudad = request.form.get("ciudad", "").strip()
        if not nombre or not ciudad:
            flash("Nombre y ciudad son obligatorios.", "error")
            return render_template("restaurantes/formulario.html", restaurante=restaurante), 400

        restaurante.nombre = nombre
        restaurante.ciudad = ciudad
        restaurante.direccion = request.form.get("direccion", "").strip() or None
        restaurante.telefono = request.form.get("telefono", "").strip() or None
        db.session.commit()
        flash("Restaurante actualizado.", "success")
        return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante.id))

    return render_template("restaurantes/formulario.html", restaurante=restaurante)


# ---------- DELETE (solo POST) ----------
@bp.post("/<int:restaurante_id>/eliminar")
def eliminar_restaurante(restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)
    try:
        db.session.delete(restaurante)
        db.session.commit()
        flash("Restaurante eliminado.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se puede eliminar: tiene pedidos asociados.", "error")
        return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante_id))
    return redirect(url_for("restaurantes.listar_restaurantes"))


# ---------- CREATE: plato dentro de un restaurante ----------
@bp.post("/<int:restaurante_id>/platos")
def agregar_plato(restaurante_id):
    restaurante = db.get_or_404(Restaurante, restaurante_id)

    nombre = request.form.get("nombre", "").strip()
    try:
        precio = Decimal(request.form.get("precio", ""))
    except InvalidOperation:
        precio = None

    if not nombre or precio is None or precio <= 0:
        flash("El plato necesita nombre y un precio mayor a 0.", "error")
        return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante.id))

    db.session.add(Plato(
        nombre=nombre,
        precio=precio,
        disponible="disponible" in request.form,   # un checkbox desmarcado no se envía
        restaurante_id=restaurante.id,
    ))
    db.session.commit()
    flash("Plato agregado.", "success")
    return redirect(url_for("restaurantes.detalle_restaurante", restaurante_id=restaurante.id))