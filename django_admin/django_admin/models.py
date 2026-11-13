from django.db import models


class Restaurante(models.Model):
    nombre = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=80)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'content"."restaurantes' # "restaurantes"
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        db_column="restaurante_id",
        related_name="platos",
    )

    class Meta:
        db_table = 'content"."platos' # "platos"
        verbose_name = "Plato"
        verbose_name_plural = "Platos"

    def __str__(self):
        return f"{self.nombre} - {self.restaurante.nombre}"

class EstadoPedido(models.TextChoices):      # a nivel de módulo, para poder usarlo en Meta
    PENDIENTE      = "pendiente", "Pendiente"
    EN_PREPARACION = "en_preparacion", "En preparación"
    LISTO          = "listo", "Listo"
    ENTREGADO      = "entregado", "Entregado"
    CANCELADO      = "cancelado", "Cancelado"


class Pedido(models.Model):
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        db_column="restaurante_id",
        related_name="pedidos",
    )
    cliente = models.CharField(max_length=255, db_index=True)   # sub del token de Auth0
    estado = models.CharField(max_length=20, choices=EstadoPedido.choices,
                              default=EstadoPedido.PENDIENTE)
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'content"."pedido'
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(estado__in=EstadoPedido.values),
                name="pedido_estado_valido",
            ),
            models.CheckConstraint(condition=models.Q(total__gte=0), name="pedido_total_no_negativo"),
        ]

    def __str__(self):
        return f"Pedido {self.id} - {self.estado}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column="pedido_id",
        related_name="items",
    )
    plato = models.ForeignKey(
        Plato, on_delete=models.PROTECT, db_column="plato_id", related_name="items"
    )
    cantidad = models.PositiveSmallIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        db_column="restaurante_id",
        related_name="items_pedido",
    )

    class Meta:
        db_table = 'content"."item_pedido'
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"
        constraints = [
            models.CheckConstraint(condition=models.Q(cantidad__gte=1, cantidad__lte=20),
                                   name="item_cantidad_1_a_20"),
            models.CheckConstraint(condition=models.Q(precio_unitario__gte=0),
                                   name="item_precio_no_negativo"),
        ]

    def __str__(self):
        return f"Item {self.id} - Plato ID: {self.plato_id}"