"""Las seis pruebas obligatorias de R6, en el orden del enunciado."""
from decimal import Decimal


def test_1_sin_sesion_crear_pedido_no_crea_nada_y_responde_401(cliente_como, contar):
    antes = contar()

    r = cliente_como(None).post("/restaurantes/1/pedir", data={"cantidad_1": "2"})

    assert r.status_code == 401          # página de "inicia sesión"
    assert contar() == antes             # ninguna fila nueva en Pedido ni ItemPedido


def test_2_cliente_que_avanza_estado_recibe_403_y_el_estado_no_cambia(
        cliente_como, crear_pedido, leer_pedido):
    pedido_id = crear_pedido(estado="pendiente")

    r = cliente_como("cliente").post(f"/cocina/{pedido_id}/avanzar",
                                     data={"estado": "en_preparacion"})

    assert r.status_code == 403          # falta update:pedidos
    assert leer_pedido(pedido_id).estado == "pendiente"


def test_3_el_total_lo_calcula_el_servidor_e_ignora_un_precio_inventado(
        cliente_como, leer_pedido):
    r = cliente_como("cliente").post("/restaurantes/1/pedir", data={
        "cantidad_1": "2",            # 2 × Salteña (8.50)
        "cantidad_2": "1",            # 1 × Silpancho (35.00)
        "precio_1": "0.01",           # precio inventado: se ignora
        "total": "1",                 # total inventado: se ignora
    })

    assert r.status_code == 302                     # Post/Redirect/Get
    pedido = leer_pedido(1)
    assert pedido.total == Decimal("52.00")         # 2×8.50 + 35.00
    assert sorted(i.precio_unitario for i in pedido.items) == [Decimal("8.50"), Decimal("35.00")]


def test_4_pedido_con_plato_no_disponible_se_rechaza_sin_dejar_filas(cliente_como, contar):
    antes = contar()

    r = cliente_como("cliente").post("/restaurantes/1/pedir", data={
        "cantidad_1": "1",            # válido
        "cantidad_3": "1",            # Trucha: NO disponible
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

    r = cliente_como("cocina").post(f"/cocina/{pedido_id}/avanzar",
                                    data={"estado": "pendiente"}, follow_redirects=True)

    assert leer_pedido(pedido_id).estado == "listo"
    assert "no puede pasar" in r.get_data(as_text=True)
