from django.contrib import admin

from .models import ItemPedido, Pedido, Plato, Restaurante


# ---------------------------------------------------------------------------
# Pedidos (R3)
# ---------------------------------------------------------------------------

class ItemPedidoInline(admin.TabularInline):
    """R3.2: los ítems se ven y se editan en línea dentro del pedido."""

    model = ItemPedido
    extra = 0                                     # sin filas vacías de más
    fields = ("plato", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("precio_unitario", "subtotal")   # R3.3: el precio no se edita a mano

    @admin.display(description="Subtotal")
    def subtotal(self, item):
        if item.pk and item.precio_unitario is not None:
            return item.precio_unitario * item.cantidad
        return "-"


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # R3.1: columnas, filtros y búsqueda
    list_display = ("id", "cliente", "restaurante", "estado", "fecha", "total")
    list_filter = ("estado", "restaurante")
    search_fields = ("cliente",)
    date_hierarchy = "fecha"
    ordering = ("-fecha", "-id")

    # R3.2 y R3.3
    inlines = [ItemPedidoInline]
    readonly_fields = ("total",)

    def save_formset(self, request, form, formset, change):
        """Antes de guardar los ítems: congela el precio y copia el restaurante.

        precio_unitario es de solo lectura, así que no viene en el formulario:
        para un ítem nuevo (o si le cambiaron el plato) se copia del plato,
        igual que hace Flask al crear un pedido.
        """
        if formset.model is ItemPedido:
            pedido = form.instance
            for item_form in formset.forms:
                if not item_form.has_changed() or item_form in formset.deleted_forms:
                    continue
                item = item_form.instance
                if item.pk is None or "plato" in item_form.changed_data:
                    item.precio_unitario = item.plato.precio
                item.restaurante_id = pedido.restaurante_id
        super().save_formset(request, form, formset, change)

    def save_related(self, request, form, formsets, change):
        """Después de guardar los ítems, recalcula el total (nadie lo edita a mano)."""
        super().save_related(request, form, formsets, change)
        pedido = form.instance
        pedido.total = sum(
            (i.precio_unitario * i.cantidad for i in pedido.items.all()), 0
        )
        pedido.save(update_fields=["total"])


# ---------------------------------------------------------------------------
# La carta (útil para el personal interno; no lo exige el enunciado)
# ---------------------------------------------------------------------------

class PlatoInline(admin.TabularInline):
    model = Plato
    extra = 0
    fields = ("nombre", "precio", "disponible")


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "ciudad", "telefono")
    search_fields = ("nombre", "ciudad")
    inlines = [PlatoInline]


@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "restaurante", "precio", "disponible")
    list_filter = ("disponible", "restaurante")
    search_fields = ("nombre",)
