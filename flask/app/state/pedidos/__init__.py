from .base import EstadoPedido, TransicionInvalida
from .cancelado import Cancelado
from .en_preparacion import EnPreparacion
from .entregado import Entregado
from .pendiente import Pendiente

# Valor guardado en la base -> clase de estado
ESTADOS = {cls.nombre: cls for cls in (Pendiente, EnPreparacion, Entregado, Cancelado)}

# Estado destino (lo que llega del <select>) -> acción que lo produce
ACCIONES = {
    EnPreparacion.nombre: "preparar",
    Entregado.nombre: "entregar",
    Cancelado.nombre: "cancelar",
}


def estado_de(pedido) -> EstadoPedido:
    """Devuelve el objeto de estado correspondiente a pedido.estado."""
    try:
        return ESTADOS[pedido.estado]()
    except KeyError:
        raise TransicionInvalida(f"Estado desconocido: '{pedido.estado}'.") from None


def cambiar_estado(pedido, nuevo):
    """Lleva el pedido al estado 'nuevo' si la transición está permitida."""
    if nuevo == pedido.estado:
        return
    accion = ACCIONES.get(nuevo)
    if accion is None:
        raise TransicionInvalida(f"No se puede pasar un pedido a '{nuevo}'.")
    getattr(estado_de(pedido), accion)(pedido)


__all__ = [
    "ESTADOS", "EstadoPedido", "TransicionInvalida", "estado_de", "cambiar_estado",
    "Pendiente", "EnPreparacion", "Entregado", "Cancelado",
]
