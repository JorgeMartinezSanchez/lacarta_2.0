from abc import ABC

from ...errors import BusinessRuleError


class TransicionInvalida(BusinessRuleError):
    """El estado actual del pedido no permite la acción pedida."""


class EstadoPedido(ABC):
    """Estado base: por defecto ninguna acción está permitida.

    Cada estado concreto sobrescribe solo las acciones que sí permite.
    """

    nombre = ""    # el valor que se guarda en Pedido.estado (igual que en el CHECK de Django)
    etiqueta = ""  # cómo se muestra en pantalla

    # --- acciones (transiciones) -----------------------------------------

    def preparar(self, pedido):
        self._denegar("preparar")

    def marcar_listo(self, pedido):
        self._denegar("marcar como listo")

    def entregar(self, pedido):
        self._denegar("entregar")

    def cancelar(self, pedido):
        self._denegar("cancelar")

    # --- consultas ---------------------------------------------------------

    def puede_modificarse(self):
        """¿Se pueden agregar, quitar o cambiar ítems? (regla 12)"""
        return False

    def es_final(self):
        return False

    # --- ayudantes ---------------------------------------------------------

    def _cambiar(self, pedido, estado_destino):
        pedido.estado = estado_destino.nombre

    def _denegar(self, accion, motivo=None):
        raise TransicionInvalida(motivo or f"No se puede {accion} un pedido {self.etiqueta.lower()}.")
