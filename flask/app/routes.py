# app/routes.py
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from .models import Restaurante, Plato, Pedido, ItemPedido

bp = Blueprint("restaurantes", __name__, url_prefix="/restaurantes")


@bp.route("/")
def listar_restaurantes():
    ciudad = request.args.get("ciudad", "").strip()
    # ... consulta (filtrando por ciudad si viene)
    return render_template("restaurantes/index.html", restaurantes=restaurantes)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear_restaurante():
    if request.method == "POST":
        # validar, guardar, flash(...)
        return redirect(url_for("restaurantes.listar_restaurantes"))
    return render_template("restaurantes/formulario.html", restaurante=None)


@bp.route("/<int:restaurante_id>")
def detalle_restaurante(restaurante_id):
    # restaurante = ... o abort(404)
    return render_template("restaurantes/detalle.html", restaurante=restaurante)


@bp.route("/<int:restaurante_id>/editar", methods=["GET", "POST"])
def editar_restaurante(restaurante_id):
    ...


@bp.route("/<int:restaurante_id>/eliminar", methods=["POST"])
def eliminar_restaurante(restaurante_id):
    ...


@bp.route("/<int:restaurante_id>/platos", methods=["POST"])
def agregar_plato(restaurante_id):
    ...