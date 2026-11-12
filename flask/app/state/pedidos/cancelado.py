from .base import EstadoPedido


class Cancelado(EstadoPedido):
    nombre = "cancelado"

    def es_final(self):
        return True
