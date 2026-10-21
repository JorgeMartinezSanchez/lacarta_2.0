from django.db import models


class Restaurante(models.Model):
    nombre = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=80)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'content"."restaurantes'
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
        db_table = 'content"."platos'
        verbose_name = "Plato"
        verbose_name_plural = "Platos"

    def __str__(self):
        return f"{self.nombre} - {self.restaurante.nombre}"


class Pedido(models.Model):
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        db_column="restaurante_id",
        related_name="pedidos",
    )
    estado = models.CharField(max_length=120)
    fecha = models.DateField()
    total = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        db_table = 'content"."pedido'
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

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
        Plato, on_delete=models.CASCADE, db_column="plato_id", related_name="items"
    )
    cantidad = models.CharField(max_length=120)
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
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

    def __str__(self):
        return f"Item {self.id} - Plato ID: {self.plato_id}"