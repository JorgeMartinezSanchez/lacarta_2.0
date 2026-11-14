"""Pruebas adicionales de R1 y R2 (no obligatorias, pero cubren lo que se revisa en la defensa)."""
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Plato


# --- R1: pedido atómico, precio congelado -----------------------------------

def test_pedido_valido_guarda_el_sub_del_token_como_cliente(cliente_como, leer_pedido):
    r = cliente_como("cliente").post("/restaurantes/1/pedir", data={"cantidad_2": "1"})

    assert r.status_code == 302 and r.headers["Location"].endswith("/pedidos/1")
    pedido = leer_pedido(1)
    assert pedido.cliente == "auth0|cliente-1"
    assert pedido.estado == "pendiente"


def test_precio_congelado_cambiar_el_plato_no_cambia_el_pedido(cliente_como, leer_pedido):
    cliente_como("cliente").post("/restaurantes/1/pedir", data={"cantidad_1": "2"})

    db.session.get(Plato, 1).precio = Decimal("99.00")   # mañana sube el precio
    db.session.commit()

    pedido = leer_pedido(1)
    assert pedido.items[0].precio_unitario == Decimal("8.50")
    assert pedido.total == Decimal("17.00")


@pytest.mark.parametrize("datos, motivo", [
    ({"cantidad_1": "1", "cantidad_4": "1"}, "plato de otro restaurante"),
    ({"cantidad_1": "21"}, "cantidad mayor a 20"),
    ({"cantidad_1": "1.5"}, "cantidad no entera"),
    ({"cantidad_99": "1"}, "plato inexistente"),
    ({}, "sin platos"),
])
def test_pedido_invalido_se_rechaza_completo(cliente_como, contar, datos, motivo):
    antes = contar()

    r = cliente_como("cliente").post("/restaurantes/1/pedir", data=datos)

    assert r.status_code == 400, motivo
    assert contar() == antes, motivo


def test_pedir_en_restaurante_inexistente_da_404(cliente_como):
    assert cliente_como("cliente").get("/restaurantes/999/pedir").status_code == 404


# --- R2: cada rol ve y hace solo lo suyo -------------------------------------

def test_la_carta_es_publica(cliente_como):
    anonimo = cliente_como(None)
    assert anonimo.get("/restaurantes/").status_code == 200
    assert anonimo.get("/restaurantes/1").status_code == 200


def test_mis_pedidos_solo_muestra_los_propios(cliente_como, crear_pedido):
    mio = crear_pedido(cliente="auth0|cliente-1")
    ajeno = crear_pedido(cliente="auth0|cliente-2")

    html = cliente_como("cliente").get("/pedidos/").get_data(as_text=True)

    assert f"/pedidos/{mio}" in html
    assert f"/pedidos/{ajeno}" not in html


def test_cliente_cancela_su_pedido_pendiente(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="pendiente")

    r = cliente_como("cliente").post(f"/pedidos/{pedido_id}/cancelar")

    assert r.status_code == 302
    assert leer_pedido(pedido_id).estado == "cancelado"


def test_cliente_no_puede_cancelar_un_pedido_en_preparacion(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="en_preparacion")

    cliente_como("cliente").post(f"/pedidos/{pedido_id}/cancelar")

    assert leer_pedido(pedido_id).estado == "en_preparacion"


def test_cliente_no_puede_cancelar_un_pedido_ajeno(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(cliente="auth0|cliente-1")

    r = cliente_como("cliente2").post(f"/pedidos/{pedido_id}/cancelar")

    assert r.status_code == 404
    assert leer_pedido(pedido_id).estado == "pendiente"


def test_cocina_avanza_por_todos_los_estados(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="pendiente")
    cocina = cliente_como("cocina")

    for siguiente in ("en_preparacion", "listo", "entregado"):
        r = cocina.post(f"/cocina/{pedido_id}/avanzar", data={"estado": siguiente})
        assert r.status_code == 302
        assert leer_pedido(pedido_id).estado == siguiente


def test_cocina_no_puede_saltarse_listo_ni_cancelar(cliente_como, crear_pedido, leer_pedido):
    en_prep = crear_pedido(estado="en_preparacion")
    pendiente = crear_pedido(estado="pendiente")
    cocina = cliente_como("cocina")

    cocina.post(f"/cocina/{en_prep}/avanzar", data={"estado": "entregado"})
    cocina.post(f"/cocina/{pendiente}/avanzar", data={"estado": "cancelado"})

    assert leer_pedido(en_prep).estado == "en_preparacion"
    assert leer_pedido(pendiente).estado == "pendiente"


def test_admin_ve_la_cola_pero_no_puede_avanzar(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="pendiente")
    admin = cliente_como("admin")

    assert admin.get("/cocina/").status_code == 200
    r = admin.post(f"/cocina/{pedido_id}/avanzar", data={"estado": "en_preparacion"})
    assert r.status_code == 403
    assert leer_pedido(pedido_id).estado == "pendiente"


@pytest.mark.parametrize("metodo, url", [
    ("get", "/pedidos/"),
    ("get", "/cocina/"),
    ("post", "/restaurantes/1/pedir"),
    ("get", "/restaurantes/nuevo"),
])
def test_usuario_sin_rol_recibe_403(cliente_como, metodo, url):
    r = getattr(cliente_como("sin_rol"), metodo)(url)
    assert r.status_code == 403
