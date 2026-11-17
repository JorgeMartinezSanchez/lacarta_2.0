"""Las seis pruebas obligatorias de R6, en el orden del enunciado."""
from decimal import Decimal


def test_1_sin_sesion_crear_pedido_no_crea_nada_y_responde_401(cliente_como, contar):
    antes = contar()

    r = cliente_como(None).post("/pedidos/", json={
        "restaurante_id": 1, "items": [{"plato_id": 1, "cantidad": 2}]})

    assert r.status_code == 401          # sin sesión
    assert "login_url" in r.get_json()   # el frontend sabe adónde mandar al usuario
    assert contar() == antes             # ninguna fila nueva en Pedido ni ItemPedido


def test_2_cliente_que_avanza_estado_recibe_403_y_el_estado_no_cambia(
        cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="pendiente")

    r = cliente_como("cliente").post(f"/cocina/{pedido_id}/avanzar",
                                     json={"estado": "en_preparacion"})

    assert r.status_code == 403          # falta update:pedidos
    assert leer_pedido(pedido_id).estado == "pendiente"


def test_3_el_total_lo_calcula_el_servidor_e_ignora_un_precio_inventado(
        cliente_como, leer_pedido):
    r = cliente_como("cliente").post("/pedidos/", json={
        "restaurante_id": 1,
        "items": [
            {"plato_id": 1, "cantidad": 2, "precio_unitario": 0.01},  # precio inventado: se ignora
            {"plato_id": 2, "cantidad": 1},
        ],
        "total": 1,                                                    # total inventado: se ignora
    })

    assert r.status_code == 201
    assert r.get_json()["total"] == 52.0            # 2×8.50 + 35.00
    pedido = leer_pedido(1)
    assert pedido.total == Decimal("52.00")
    assert sorted(i.precio_unitario for i in pedido.items) == [Decimal("8.50"), Decimal("35.00")]


def test_4_pedido_con_plato_no_disponible_se_rechaza_sin_dejar_filas(cliente_como, contar):
    antes = contar()

    r = cliente_como("cliente").post("/pedidos/", json={
        "restaurante_id": 1,
        "items": [
            {"plato_id": 1, "cantidad": 1},   # válido
            {"plato_id": 3, "cantidad": 1},   # Trucha: NO disponible
        ],
    })

    assert r.status_code == 400
    assert contar() == antes          # ni el pedido ni el ítem válido quedaron en la base


def test_5_cliente_que_abre_el_pedido_de_otro_cliente_recibe_404(cliente_como, crear_pedido):
    pedido_ajeno = crear_pedido(cliente="auth0|cliente-1")

    r = cliente_como("cliente2").get(f"/pedidos/{pedido_ajeno}")

    assert r.status_code == 404       # 404 y no 403: no confirma que el pedido existe


def test_6_la_cocina_no_puede_pasar_un_pedido_de_listo_a_pendiente(
        cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="listo")

    r = cliente_como("cocina").post(f"/cocina/{pedido_id}/avanzar", json={"estado": "pendiente"})

    assert r.status_code == 400
    assert leer_pedido(pedido_id).estado == "listo"
    assert "no puede pasar" in r.get_json()["mensaje"]
