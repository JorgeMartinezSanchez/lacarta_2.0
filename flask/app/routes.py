from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..controllers.restaurante_controller import RestauranteController
from ..auth import requires_auth

bp = Blueprint("restaurantes", __name__, url_prefix="/restaurantes")


@bp.get("/")
def listar_restaurantes():
    ciudad = request.args.get("ciudad", "").strip()

    restaurantes = RestauranteController.listar(ciudad)

    return render_template(
        "restaurantes/index.html",
        restaurantes=restaurantes
    )


@bp.get("/<int:restaurante_id>")
def detalle_restaurante(restaurante_id):
    restaurante = RestauranteController.obtener(restaurante_id)

    return render_template(
        "restaurantes/detalle.html",
        restaurante=restaurante
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@requires_auth("write:carta")
def crear_restaurante(payload):
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "ciudad": request.form.get("ciudad", "").strip(),
            "direccion": request.form.get("direccion", "").strip(),
            "telefono": request.form.get("telefono", "").strip()
        }

        try:
            restaurante = RestauranteController.crear(datos)

            flash("Restaurante creado.", "success")

            return redirect(url_for(
                "restaurantes.detalle_restaurante",
                restaurante_id=restaurante.id
            ))

        except ValueError as error:
            flash(str(error), "error")

    return render_template(
        "restaurantes/formulario.html",
        restaurante=None
    )