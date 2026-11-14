"""Fixtures de las pruebas (R6).

- La base es SQLite en memoria, vacía en cada prueba. En producción Flask no crea
  tablas (Django es el dueño del esquema), pero en una base de prueba sí se puede.
- Auth0 NO se llama: se reemplaza verify_decode_jwt por una función que devuelve
  el payload de un usuario de prueba, con los permisos exactos del enunciado.
  El decorador @requires_auth sigue funcionando igual (lee la sesión, pide el
  payload y revisa el permiso), así que si alguien quita un decorador, la prueba
  que protege esa ruta falla.
"""
import os
from decimal import Decimal

# Config lee DATABASE_URL al importarse: se fija ANTES de importar la app.
# (load_dotenv no pisa variables que ya existen, así que el .env real no se usa.)
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from sqlalchemy import event, func, select

from app import create_app
from app.auth import decorators
from app.config import Config
from app.extensions import db
from app.models import ItemPedido, Pedido, Plato, Restaurante


class ConfigPruebas(Config):
    TESTING = True
    SECRET_KEY = "clave-de-pruebas"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SESSION_COOKIE_SECURE = False   # el cliente de pruebas usa http://
    BEHIND_PROXY = False
    AUTH0_DOMAIN = "pruebas.auth0.com"
    AUTH0_AUDIENCE = "lacarta-pruebas"
    AUTH0_CLIENT_ID = "id-de-pruebas"
    AUTH0_CLIENT_SECRET = "secreto-de-pruebas"


# Payloads de token simulados: mismos permisos que la tabla de R2.2.
USUARIOS = {
    "cliente":  {"sub": "auth0|cliente-1", "permissions": ["create:pedidos", "read:mis-pedidos"]},
    "cliente2": {"sub": "auth0|cliente-2", "permissions": ["create:pedidos", "read:mis-pedidos"]},
    "cocina":   {"sub": "auth0|cocina-1", "permissions": ["read:pedidos", "update:pedidos"]},
    "admin":    {"sub": "auth0|admin-1", "permissions": ["read:pedidos", "write:carta", "delete:carta"]},
    "sin_rol":  {"sub": "auth0|nuevo-1", "permissions": []},
}


@pytest.fixture(autouse=True)
def auth0_simulado(monkeypatch):
    """El 'token' guardado en la sesión es el nombre del usuario de prueba."""
    monkeypatch.setattr(decorators, "verify_decode_jwt", lambda token: USUARIOS[token])


@pytest.fixture
def app():
    app = create_app(ConfigPruebas)
    with app.app_context():
        # Los modelos usan el esquema "content" (como Postgres): en SQLite se
        # simula adjuntando una segunda base en memoria con ese nombre.
        event.listen(db.engine, "connect",
                     lambda conn, _: conn.execute("ATTACH DATABASE ':memory:' AS content"))
        db.engine.dispose()
        db.create_all()
        _cargar_carta()
        yield app
        db.session.remove()
        db.drop_all()


def _cargar_carta():
    """Restaurante 1 con 3 platos (uno no disponible) y restaurante 2 con 1 plato."""
    r1 = Restaurante(id=1, nombre="La Casona", ciudad="La Paz")
    r2 = Restaurante(id=2, nombre="El Fogón", ciudad="Santa Cruz")
    db.session.add_all([r1, r2])
    db.session.add_all([
        Plato(id=1, nombre="Salteña", precio=Decimal("8.50"), disponible=True, restaurante_id=1),
        Plato(id=2, nombre="Silpancho", precio=Decimal("35.00"), disponible=True, restaurante_id=1),
        Plato(id=3, nombre="Trucha", precio=Decimal("48.00"), disponible=False, restaurante_id=1),
        Plato(id=4, nombre="Majadito", precio=Decimal("40.00"), disponible=True, restaurante_id=2),
    ])
    db.session.commit()


@pytest.fixture
def cliente_como(app):
    """cliente_como("cocina") -> cliente HTTP con la sesión de ese usuario.
    cliente_como(None) -> cliente sin sesión."""
    def _crear(usuario=None):
        client = app.test_client()
        if usuario:
            with client.session_transaction() as sesion:
                sesion["access_token"] = usuario
        return client
    return _crear


@pytest.fixture
def contar():
    """Devuelve (filas en Pedido, filas en ItemPedido)."""
    def _contar():
        return (db.session.scalar(select(func.count()).select_from(Pedido)),
                db.session.scalar(select(func.count()).select_from(ItemPedido)))
    return _contar


@pytest.fixture
def crear_pedido():
    """Inserta un pedido directo en la base (para preparar escenarios)."""
    def _crear(cliente="auth0|cliente-1", estado="pendiente", restaurante_id=1):
        from datetime import date
        pedido = Pedido(cliente=cliente, restaurante_id=restaurante_id, estado=estado,
                        fecha=date.today(), total=Decimal("17.00"),
                        items=[ItemPedido(plato_id=1, cantidad=2, precio_unitario=Decimal("8.50"),
                                          restaurante_id=restaurante_id)])
        db.session.add(pedido)
        db.session.commit()
        return pedido.id
    return _crear


@pytest.fixture
def leer_pedido():
    """Lee el pedido tal como quedó en la base (o None si no existe)."""
    def _leer(pedido_id):
        db.session.expire_all()   # no usar lo que quedó en memoria
        return db.session.get(Pedido, pedido_id)
    return _leer
