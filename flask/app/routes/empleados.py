"""Controlador de empleados (capa de presentación).

Solo hace tres cosas: leer la petición, llamar al servicio y responder
(render_template / redirect / flash). No toca db ni modelos.
Todas las rutas son privadas: los empleados tienen datos personales (CI, teléfono).
"""
from dataclasses import asdict

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..auth import requires_auth
from ..dtos.empleados_dtos import EmpleadoDTO_Input
from ..errors import BusinessRuleError, NotFoundError
from .dependencias import empleados_service

bp = Blueprint("empleados", __name__, url_prefix="/empleados")


def _dto_desde_form() -> EmpleadoDTO_Input:
    return EmpleadoDTO_Input(
        primer_nombre=request.form.get("primer_nombre", ""),
        segundo_nombre=request.form.get("segundo_nombre"),
        apellido=request.form.get("apellido", ""),
        ci=request.form.get("ci", ""),
        telefono=request.form.get("telefono", ""),
        email=request.form.get("email", ""),
    )


@bp.get("/")
@requires_auth("read:empleados")
def listar_empleados(payload):
    empleados = empleados_service().get_all_empleados()
    return render_template("empleados/index.html", empleados=empleados)


@bp.get("/<int:empleado_id>")
@requires_auth("read:empleados")
def detalle_empleado(payload, empleado_id):
    try:
        empleado = empleados_service().get_empleado(empleado_id)
    except NotFoundError:
        abort(404)
    return render_template("empleados/detalle.html", empleado=empleado)


@bp.route("/nuevo", methods=["GET", "POST"])
@requires_auth("write:empleados")
def crear_empleado(payload):
    if request.method == "POST":
        try:
            empleado = empleados_service().create_empleado(_dto_desde_form())
        except BusinessRuleError as e:
            flash(str(e), "error")
            # Se vuelve a mostrar lo que escribió el usuario para que no lo pierda.
            return render_template("empleados/formulario.html", empleado_id=None,
                                   valores=request.form), 400
        flash("Empleado creado.", "success")
        return redirect(url_for("empleados.detalle_empleado", empleado_id=empleado.id))

    return render_template("empleados/formulario.html", empleado_id=None, valores={})


@bp.route("/<int:empleado_id>/editar", methods=["GET", "POST"])
@requires_auth("write:empleados")
def editar_empleado(payload, empleado_id):
    service = empleados_service()
    try:
        if request.method == "POST":
            service.update_empleado(empleado_id, _dto_desde_form())
            flash("Empleado actualizado.", "success")
            return redirect(url_for("empleados.detalle_empleado", empleado_id=empleado_id))
        empleado = service.get_empleado(empleado_id)
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
        return render_template("empleados/formulario.html", empleado_id=empleado_id,
                               valores=request.form), 400
    return render_template("empleados/formulario.html", empleado_id=empleado_id,
                           valores=asdict(empleado))


@bp.post("/<int:empleado_id>/eliminar")
@requires_auth("delete:empleados")
def eliminar_empleado(payload, empleado_id):
    try:
        empleados_service().delete_empleado(empleado_id)
    except NotFoundError:
        abort(404)
    except BusinessRuleError as e:
        flash(str(e), "error")
        return redirect(url_for("empleados.detalle_empleado", empleado_id=empleado_id))
    flash("Empleado eliminado.", "success")
    return redirect(url_for("empleados.listar_empleados"))
