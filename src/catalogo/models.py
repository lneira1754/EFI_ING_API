from django.core.validators import MinValueValidator
from django.db import models


class Marca(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    pais_origen = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Material(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class TipoLente(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    precio_adicional = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
    )
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tipo de Lente"
        verbose_name_plural = "Tipos de Lentes"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} (+${self.precio_adicional})"


class Anteojo(models.Model):
    class Forma(models.TextChoices):
        REDONDO = "redondo", "Redondo"
        RECTANGULAR = "rectangular", "Rectangular"
        AVIADOR = "aviador", "Aviador"
        CAT_EYE = "cat_eye", "Cat Eye"
        WAYFARER = "wayfarer", "Wayfarer"
        HEXAGONAL = "hexagonal", "Hexagonal"
        OTRO = "otro", "Otro"

    class Genero(models.TextChoices):
        UNISEX = "unisex", "Unisex"
        HOMBRE = "hombre", "Hombre"
        MUJER = "mujer", "Mujer"
        NINOS = "ninos", "Niños"

    nombre = models.CharField(max_length=160)
    sku = models.CharField(max_length=50, unique=True)
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name="anteojos",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="anteojos",
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="anteojos",
    )
    tipos_lente = models.ManyToManyField(
        TipoLente,
        related_name="anteojos",
        blank=True,
    )
    forma = models.CharField(
        max_length=30,
        choices=Forma.choices,
        default=Forma.WAYFARER,
    )
    genero = models.CharField(
        max_length=20,
        choices=Genero.choices,
        default=Genero.UNISEX,
    )
    color_marco = models.CharField(max_length=80)
    color_lente = models.CharField(max_length=80, blank=True)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anteojo"
        verbose_name_plural = "Anteojos"
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.nombre} ({self.sku})"


class ImagenAnteojo(models.Model):
    anteojo = models.ForeignKey(
        Anteojo,
        on_delete=models.CASCADE,
        related_name="imagenes",
    )
    imagen = models.ImageField(upload_to="anteojos/")
    es_modelo = models.BooleanField(
        default=False,
        help_text="Indica si la foto muestra a una persona usando el anteojo",
    )
    orden = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen de Anteojo"
        verbose_name_plural = "Imágenes de Anteojos"
        ordering = ["orden", "id"]

    def __str__(self):
        tipo = "Modelo" if self.es_modelo else "Producto"
        return f"Imagen {tipo} de {self.anteojo.nombre}"
