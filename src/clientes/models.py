from django.contrib.auth.models import User
from django.db import models


class Cliente(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cliente",
    )
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=250, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["-creado"]

    def __str__(self):
        nombre_completo = self.usuario.get_full_name()
        if nombre_completo:
            return f"{nombre_completo} (DNI {self.dni})"
        return f"{self.usuario.username} (DNI {self.dni})"


class Optometrista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    especialidad = models.CharField(max_length=120, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Optometrista"
        verbose_name_plural = "Optometristas"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"Dr/a. {self.apellido}, {self.nombre} (Mat. {self.matricula})"


class Receta(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="recetas",
    )
    optometrista = models.ForeignKey(
        Optometrista,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recetas",
    )
    fecha_emision = models.DateField()
    # Ojo derecho (OD)
    od_esfera = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    od_cilindro = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    od_eje = models.PositiveIntegerField(default=0, help_text="Grados de 0 a 180")
    # Ojo izquierdo (OI)
    oi_esfera = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    oi_cilindro = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    oi_eje = models.PositiveIntegerField(default=0, help_text="Grados de 0 a 180")
    # Adicion y distancia pupilar
    adicion = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    distancia_pupilar = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="En milímetros (mm)",
    )
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ["-fecha_emision", "-id"]

    def __str__(self):
        return f"Receta #{self.id} de {self.cliente} ({self.fecha_emision})"


class Turno(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADO = "confirmado", "Confirmado"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="turnos",
    )
    optometrista = models.ForeignKey(
        Optometrista,
        on_delete=models.PROTECT,
        related_name="turnos",
    )
    fecha_hora = models.DateTimeField()
    motivo = models.CharField(max_length=200, default="Consulta visual general")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"Turno {self.fecha_hora.strftime('%d/%m/%Y %H:%M')} - {self.cliente}"
