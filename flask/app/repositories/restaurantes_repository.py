
from datetime import date
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from .extensions import db
from .models import Restaurante, Plato, Pedido, ItemPedido


class RestaurantesRepository:

    # ---------- READ: restaurantes ----------

    @staticmethod
    def get_restaurantes():
        return Restaurante.query.all()

    # ---------- READ: platos de un restaurante ----------

    @staticmethod
    def get_platos(restaurante_id):
        return Plato.query.filter_by(
            restaurante_id=restaurante_id
        ).all()

    # ---------- CREATE: pedido ----------

    @staticmethod
    def create_pedido(restaurante_id, items, fecha=None):
        try:
            if not restaurante_id or not items:
                raise ValueError("Missing restaurante_id or items")

            pedido = Pedido(
                restaurante_id=restaurante_id,
                estado="pendiente",
                fecha=fecha or date.today(),
                total=Decimal("0"),
            )

            db.session.add(pedido)
            db.session.flush()  # Obtiene pedido.id sin confirmar la transacción

            total = Decimal("0")

            for item in items:
                plato_id = item.get("plato_id")
                cantidad = int(item.get("cantidad", 1))

                if not plato_id or cantidad < 1:
                    raise ValueError(
                        "Item inválido: plato_id o cantidad incorrectos"
                    )

                plato = db.session.get(Plato, plato_id)

                if plato is None or plato.restaurante_id != restaurante_id:
                    raise ValueError(
                        f"El plato {plato_id} no existe en este restaurante"
                    )

                if not plato.disponible:
                    raise ValueError(
                        f"El plato {plato.nombre} no está disponible"
                    )

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

            pedido.total = total

            db.session.commit()

            return pedido

        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            raise
