from .base import EstadoPedido, TransicionInvalida
from .cancelado import Cancelado
from .en_preparacion import EnPreparacion
from .entregado import Entregado
from .listo import Listo
from .pendiente import Pendiente

#   pendiente ──► en_preparacion ──► listo ──► entregado
#       └──────────────────────────────────────► cancelado

# En el orden del flujo (para los <select> de los templates)
ORDEN = (Pendiente, EnPreparacion, Listo, Entregado, Cancelado)

# Valor guardado en la base -> clase de estado
ESTADOS = {cls.nombre: cls for cls in ORDEN}

# Para los templates: [("pendiente", "Pendiente"), ("en_preparacion", "En preparación"), ...]
OPCIONES = [(cls.nombre, cls.etiqueta) for cls in ORDEN]

# La cola de la cocina: pedidos que todavía no terminaron
ACTIVOS = (Pendiente.nombre, EnPreparacion.nombre, Listo.nombre)

# Siguiente estado de cada pedido activo (el botón "Pasar a ..." de la cocina)
SIGUIENTE = {
    Pendiente.nombre: EnPreparacion,
    EnPreparacion.nombre: Listo,
    Listo.nombre: Entregado,
}

# Estados a los que la cocina puede llevar un pedido (cancelar es solo del cliente dueño)
DESTINOS_COCINA = (EnPreparacion.nombre, Listo.nombre, Entregado.nombre)

# Estado destino (lo que llega del formulario) -> acción que lo produce
ACCIONES = {
    EnPreparacion.nombre: "preparar",
    Listo.nombre: "marcar_listo",
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
    "ACCIONES", "ACTIVOS", "DESTINOS_COCINA", "ESTADOS", "OPCIONES", "ORDEN", "SIGUIENTE",
    "EstadoPedido", "TransicionInvalida", "estado_de", "cambiar_estado",
    "Pendiente", "EnPreparacion", "Listo", "Entregado", "Cancelado",
]
