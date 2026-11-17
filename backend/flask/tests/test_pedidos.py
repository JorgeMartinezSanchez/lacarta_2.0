"""Pruebas adicionales de R1 y R2 (no obligatorias, pero cubren lo que se revisa en la defensa)."""
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Plato


def _pedido(*items, restaurante_id=1):
    """_pedido((1, 2), (2, 1)) -> cuerpo JSON con 2 × plato 1 y 1 × plato 2."""
    return {"restaurante_id": restaurante_id,
            "items": [{"plato_id": p, "cantidad": c} for p, c in items]}


# --- R1: pedido atómico, precio congelado -----------------------------------

def test_pedido_valido_guarda_el_sub_del_token_como_cliente(cliente_como, leer_pedido):
    r = cliente_como("cliente").post("/pedidos/", json=_pedido((2, 1)))

    assert r.status_code == 201
    datos = r.get_json()
    assert datos["id"] == 1 and datos["estado"] == "pendiente"
    pedido = leer_pedido(1)
    assert pedido.cliente == "auth0|cliente-1"
    assert pedido.estado == "pendiente"


def test_precio_congelado_cambiar_el_plato_no_cambia_el_pedido(cliente_como, leer_pedido):
    cliente_como("cliente").post("/pedidos/", json=_pedido((1, 2)))

    db.session.get(Plato, 1).precio = Decimal("99.00")   # mañana sube el precio
    db.session.commit()

    pedido = leer_pedido(1)
    assert pedido.items[0].precio_unitario == Decimal("8.50")
    assert pedido.total == Decimal("17.00")


@pytest.mark.parametrize("cuerpo, motivo", [
    (_pedido((1, 1), (4, 1)), "plato de otro restaurante"),
    (_pedido((1, 21)), "cantidad mayor a 20"),
    (_pedido((1, "1.5")), "cantidad no entera (texto)"),
    (_pedido((1, 1.5)), "cantidad no entera (número)"),
    (_pedido((99, 1)), "plato inexistente"),
    (_pedido(), "sin platos"),
    ({"restaurante_id": 1, "items": "1"}, "items no es una lista"),
    ({"restaurante_id": 1, "items": [{"plato_id": "x", "cantidad": 1}]}, "plato_id inválido"),
])
def test_pedido_invalido_se_rechaza_completo(cliente_como, contar, cuerpo, motivo):
    antes = contar()

    r = cliente_como("cliente").post("/pedidos/", json=cuerpo)

    assert r.status_code == 400, motivo
    assert "mensaje" in r.get_json(), motivo
    assert contar() == antes, motivo


def test_pedido_sin_cuerpo_json_da_400(cliente_como, contar):
    antes = contar()
    r = cliente_como("cliente").post("/pedidos/", data={"cantidad_1": "1"})  # formulario, no JSON
    assert r.status_code == 400
    assert contar() == antes


def test_pedir_en_restaurante_inexistente_da_404(cliente_como):
    r = cliente_como("cliente").post("/pedidos/", json=_pedido((1, 1), restaurante_id=999))
    assert r.status_code == 404


# --- R2: cada rol ve y hace solo lo suyo -------------------------------------

def test_la_carta_es_publica(cliente_como):
    anonimo = cliente_como(None)
    lista = anonimo.get("/restaurantes/")
    detalle = anonimo.get("/restaurantes/1")

    assert lista.status_code == 200 and len(lista.get_json()) == 2
    assert detalle.status_code == 200
    assert detalle.get_json()["nombre"] == "La Casona"
    assert len(detalle.get_json()["platos"]) == 3


def test_mis_pedidos_solo_muestra_los_propios(cliente_como, crear_pedido):
    mio = crear_pedido(cliente="auth0|cliente-1")
    ajeno = crear_pedido(cliente="auth0|cliente-2")

    ids = [p["id"] for p in cliente_como("cliente").get("/pedidos/").get_json()]

    assert mio in ids
    assert ajeno not in ids


def test_cliente_cancela_su_pedido_pendiente(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="pendiente")

    r = cliente_como("cliente").post(f"/pedidos/{pedido_id}/cancelar")

    assert r.status_code == 200
    assert r.get_json()["estado"] == "cancelado"
    assert leer_pedido(pedido_id).estado == "cancelado"


def test_cliente_no_puede_cancelar_un_pedido_en_preparacion(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="en_preparacion")

    r = cliente_como("cliente").post(f"/pedidos/{pedido_id}/cancelar")

    assert r.status_code == 400
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
        r = cocina.post(f"/cocina/{pedido_id}/avanzar", json={"estado": siguiente})
        assert r.status_code == 200
        assert r.get_json()["estado"] == siguiente
        assert leer_pedido(pedido_id).estado == siguiente


def test_cola_de_cocina_indica_el_siguiente_estado(cliente_como, crear_pedido):
    crear_pedido(estado="pendiente")

    cola = cliente_como("cocina").get("/cocina/").get_json()

    assert cola[0]["siguiente"] == {"estado": "en_preparacion", "etiqueta": "En preparación"}


def test_cocina_no_puede_saltarse_listo_ni_cancelar(cliente_como, crear_pedido, leer_pedido):
    en_prep = crear_pedido(estado="en_preparacion")
    pendiente = crear_pedido(estado="pendiente")
    cocina = cliente_como("cocina")

    r1 = cocina.post(f"/cocina/{en_prep}/avanzar", json={"estado": "entregado"})
    r2 = cocina.post(f"/cocina/{pendiente}/avanzar", json={"estado": "cancelado"})

    assert r1.status_code == r2.status_code == 400
    assert leer_pedido(en_prep).estado == "en_preparacion"
    assert leer_pedido(pendiente).estado == "pendiente"


def test_admin_ve_la_cola_pero_no_puede_avanzar(cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="pendiente")
    admin = cliente_como("admin")

    assert admin.get("/cocina/").status_code == 200
    r = admin.post(f"/cocina/{pedido_id}/avanzar", json={"estado": "en_preparacion"})
    assert r.status_code == 403
    assert leer_pedido(pedido_id).estado == "pendiente"


@pytest.mark.parametrize("metodo, url", [
    ("get", "/pedidos/"),
    ("get", "/cocina/"),
    ("post", "/pedidos/"),
    ("post", "/restaurantes/"),
    ("put", "/platos/1"),
    ("delete", "/restaurantes/1"),
])
def test_usuario_sin_rol_recibe_403(cliente_como, metodo, url):
    r = getattr(cliente_como("sin_rol"), metodo)(url, json={})
    assert r.status_code == 403
    assert r.get_json()["error"] == "forbidden"


# --- Carta (admin) y formato de las respuestas ------------------------------

def test_admin_crea_edita_y_elimina_un_plato(cliente_como):
    admin = cliente_como("admin")

    r = admin.post("/platos/", json={"restaurante_id": 2, "nombre": "Pique", "precio": "55.5"})
    assert r.status_code == 201
    plato = r.get_json()
    assert plato["precio"] == 55.5 and plato["disponible"] is True

    r = admin.put(f"/platos/{plato['id']}", json={"nombre": "Pique macho", "precio": 60,
                                                   "disponible": False, "restaurante_id": 1})
    assert r.status_code == 200
    assert r.get_json()["nombre"] == "Pique macho"
    assert r.get_json()["restaurante_id"] == 2        # no se cambia de restaurante

    assert admin.delete(f"/platos/{plato['id']}").status_code == 200
    assert admin.get(f"/platos/{plato['id']}").status_code == 404


def test_tipo_incorrecto_en_el_cuerpo_da_400_y_no_500(cliente_como):
    r = cliente_como("admin").post("/restaurantes/", json={"nombre": ["x"], "ciudad": "La Paz"})
    assert r.status_code == 400


def test_errores_tambien_son_json(cliente_como):
    r = cliente_como(None).get("/no-existe")
    assert r.status_code == 404
    assert r.is_json and r.get_json()["error"] == "not_found"


def test_fechas_en_formato_iso(cliente_como, crear_pedido):
    from datetime import date
    pedido_id = crear_pedido()
    r = cliente_como("cliente").get(f"/pedidos/{pedido_id}")
    assert r.get_json()["fecha"] == date.today().isoformat()
