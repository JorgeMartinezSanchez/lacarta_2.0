from .base import EstadoPedido


class Entregado(EstadoPedido):
    nombre = "entregado"

    def es_final(self):
        return True
