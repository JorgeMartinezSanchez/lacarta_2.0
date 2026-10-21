from flask import Blueprint, jsonify, request
from .auth import require_auth
from .extensions import db
from .models import Restaurante, Plato, Pedido, ItemPedido

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.get("/restaurantes")
@require_auth
def get_restaurantes():
    restaurantes = Restaurante.query.all()
    return jsonify([{
        "id": r.id,
        "nombre": r.nombre,
        "ciudad": r.ciudad,
        "direccion": r.direccion,
        "telefono": r.telefono
    } for r in restaurantes])

@bp.get("/restaurantes/<int:restaurante_id>/platos")
@require_auth
def get_platos(restaurante_id):
    platos = Plato.query.filter_by(restaurante_id=restaurante_id).all()
    return jsonify([{
        "id": p.id,
        "nombre": p.nombre,
        "precio": str(p.precio),
        "disponible": p.disponible
    } for p in platos])

@bp.post("/pedidos")
@require_auth
def create_pedido():
    try:
        data = request.get_json() or {}
        restaurante_id = data.get("restaurante_id")
        items = data.get("items", [])

        if not restaurante_id or not items:
            return jsonify({"error": "Missing restaurante_id or items"}), 400

        fecha_str = data.get("fecha")
        fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()

        pedido = Pedido(
            restaurante_id=restaurante_id,
            estado="pendiente",
            fecha=fecha,
            total=Decimal("0"),
        )
        db.session.add(pedido)
        db.session.flush()  # obtiene pedido.id sin confirmar la transacción

        total = Decimal("0")
        for item in items:
            plato_id = item.get("plato_id")
            cantidad = int(item.get("cantidad", 1))

            if not plato_id or cantidad < 1:
                raise ValueError("Item inválido: plato_id o cantidad incorrectos")

            plato = db.session.get(Plato, plato_id)
            if plato is None or plato.restaurante_id != restaurante_id:
                raise ValueError(f"El plato {plato_id} no existe en este restaurante")
            if not plato.disponible:
                raise ValueError(f"El plato {plato.nombre} no está disponible")

            db.session.add(
                ItemPedido(
                    pedido_id=pedido.id,
                    plato_id=plato.id,
                    cantidad=cantidad,
                    precio_unitario=plato.precio,
                    restaurante_id=restaurante_id,
                )
            )
            total += plato.precio * cantidad

        pedido.total = total  # calculado en el servidor, no confiado al cliente
        db.session.commit()   # único commit: todo o nada

        return jsonify({"message": "Pedido created", "pedido_id": pedido.id}), 201

    except ValueError as e:  # datos inválidos (fecha, cantidad, plato)
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    except SQLAlchemyError as e:  # errores de base de datos
        db.session.rollback()
        return jsonify({"error": "Database error", "detail": str(e)}), 500

    finally:
        db.session.close()  # libera la conexión pase lo que pase