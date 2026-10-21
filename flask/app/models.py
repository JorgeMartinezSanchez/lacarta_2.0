from flask_sqlalchemy import SQLAlchemy
from .extensions import db

class Restaurante(db.Model):
    __tablename__ = "restaurantes"
    __table_args__ = {"schema": "content"}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    ciudad = db.Column(db.String(80), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(30))

    platos = db.relationship(
        "Plato",
        backref="restaurante",
        cascade="all, delete-orphan",   # al borrar el restaurante, borra sus platos
        order_by="Plato.nombre",
    )


class Plato(db.Model):
  __tablename__ = "platos"
  __table_args__ = {"schema": "content"}

  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(120), nullable=False)
  precio = db.Column(db.Numeric(10, 2), nullable=False)
  disponible = db.Column(db.Boolean, default=True)
  restaurante_id = db.Column(
      db.Integer,
      db.ForeignKey("content.restaurantes.id"),
      nullable=False,
  )


class Pedido(db.Model):
  __tablename__ = "pedido"
  __table_args__ = {"schema": "content"}

  id = db.Column(db.Integer, primary_key=True)
  restaurante_id = db.Column(
      db.Integer,
      db.ForeignKey("content.restaurantes.id"),
      nullable=False,
  )
  estado = db.Column(db.String(120), nullable=False, default="pendiente")
  fecha = db.Column(db.Date, nullable=False)
  total = db.Column(db.Numeric(10, 2))


class ItemPedido(db.Model):
  __tablename__ = "item_pedido"
  __table_args__ = {"schema": "content"}

  id = db.Column(db.Integer, primary_key=True)
  pedido_id = db.Column(
      db.Integer, db.ForeignKey("content.pedido.id"), nullable=False
  )
  plato_id = db.Column(
      db.Integer, db.ForeignKey("content.platos.id"), nullable=False
  )
  cantidad = db.Column(db.String(120), nullable=False)
  precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
  restaurante_id = db.Column(
      db.Integer,
      db.ForeignKey("content.restaurantes.id"),
      nullable=False,
  )