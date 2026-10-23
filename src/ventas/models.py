from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from catalogo.models import Anteojo, TipoLente
from clientes.models import Cliente, Receta


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADO = "pagado", "Pagado"
        ENVIADO = "enviado", "Enviado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    receta = models.ForeignKey(
        Receta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        help_text="Receta médica asociada si los lentes son graduados",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado"]

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente} ({self.get_estado_display()})"

    def calcular_total(self):
        total = sum(item.subtotal for item in self.detalles.all())
        self.total = total
        return total


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    anteojo = models.ForeignKey(
        Anteojo,
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    tipo_lente = models.ForeignKey(
        TipoLente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detalles_pedido",
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"

    def __str__(self):
        return f"{self.cantidad}x {self.anteojo.nombre} (Pedido #{self.pedido_id})"

    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            base = self.anteojo.precio
            adicional = self.tipo_lente.precio_adicional if self.tipo_lente else 0
            self.precio_unitario = base + adicional
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


class Resena(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    anteojo = models.ForeignKey(
        Anteojo,
        on_delete=models.CASCADE,
        related_name="resenas",
    )
    puntaje = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas",
    )
    comentario = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ["-creado"]
        constraints = [
            models.UniqueConstraint(
                fields=["cliente", "anteojo"],
                name="unica_resena_por_cliente_anteojo",
            )
        ]

    def __str__(self):
        return f"Reseña de {self.cliente} para {self.anteojo.nombre}: {self.puntaje}★"
