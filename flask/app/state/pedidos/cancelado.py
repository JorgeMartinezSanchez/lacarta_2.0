from .base import EstadoPedido


class Cancelado(EstadoPedido):
    nombre = "cancelado"
    etiqueta = "Cancelado"

    def es_final(self):
        return True
