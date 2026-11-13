from .base import EstadoPedido


class Entregado(EstadoPedido):
    nombre = "entregado"
    etiqueta = "Entregado"

    def es_final(self):
        return True
