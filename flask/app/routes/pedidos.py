from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from ..models import db, Pedido, Restaurante
from ..auth import requires_auth

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@bp.get("/")
@requires_auth("read:pedidos")
def listar_pedidos():
    estado = request.args.get("estado", "").strip()
    consulta = Pedido.query.order_by(Pedido.fecha.desc())
    if estado:
        consulta = consulta.filter(Pedido.estado == estado)
    return render_template("pedidos/index.html", pedidos=consulta.all())


@bp.get("/<int:pedido_id>")
@requires_auth("read:pedidos")
def detalle_pedido(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    return render_template("pedidos/detalle.html", pedido=pedido)


@bp.route("/nuevo", methods=["GET", "POST"])
@requires_auth("create:pedidos")
def crear_pedido(payload):
    if request.method == "POST":
        restaurante_id = request.form.get("restaurante_id", type=int)
        restaurante = db.session.get(Restaurante, restaurante_id) if restaurante_id else None
        if restaurante is None:
            flash("Debes elegir un restaurante válido.", "error")
            return render_template("pedidos/formulario.html",
                                   pedido=None,
                                   restaurantes=Restaurante.query.order_by(Restaurante.nombre).all()), 400

        pedido = Pedido(
            restaurante_id=restaurante.id,
            estado=request.form.get("estado", "pendiente").strip() or "pendiente",
            fecha=date.today(),
            total=None,
        )
        db.session.add(pedido)
        db.session.commit()
        flash("Pedido creado.", "success")
        return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))

    # GET: permitir preseleccionar restaurante vía ?restaurante_id=
    restaurante_preseleccionado = request.args.get("restaurante_id", type=int)

    return render_template("pedidos/formulario.html",
                           pedido=None,
                           restaurante_preseleccionado=restaurante_preseleccionado,
                           restaurantes=Restaurante.query.order_by(Restaurante.nombre).all())


@bp.post("/<int:pedido_id>/estado")
@requires_auth("write:pedidos")
def actualizar_estado(payload, pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    nuevo = request.form.get("estado", "").strip()
    if not nuevo:
        flash("Estado inválido.", "error")
    else:
        pedido.estado = nuevo
        db.session.commit()
        flash("Estado actualizado.", "success")
    return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido.id))


@bp.post("/<int:pedido_id>/eliminar")
@requires_auth("delete:pedidos")
def eliminar_pedido(payload, pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    try:
        db.session.delete(pedido)
        db.session.commit()
        flash("Pedido eliminado.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("No se puede eliminar: tiene items asociados.", "error")
        return redirect(url_for("pedidos.detalle_pedido", pedido_id=pedido_id))
    return redirect(url_for("pedidos.listar_pedidos"))