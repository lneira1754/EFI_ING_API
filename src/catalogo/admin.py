from django.contrib import admin
from django.utils.html import format_html
from .models import Anteojo, Categoria, ImagenAnteojo, Marca, Material, TipoLente


class ImagenAnteojoInline(admin.TabularInline):
    model = ImagenAnteojo
    extra = 1
    fields = ["imagen", "es_modelo", "orden", "vista_previa"]
    readonly_fields = ["vista_previa"]

    def vista_previa(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="height: 50px; border-radius: 4px;" />',
                obj.imagen.url,
            )
        return "-"
    vista_previa.short_description = "Vista previa"


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "pais_origen", "activo", "creado"]
    list_filter = ["activo", "pais_origen"]
    search_fields = ["nombre", "pais_origen"]
    ordering = ["nombre"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "slug", "activo", "creado"]
    list_filter = ["activo"]
    search_fields = ["nombre", "slug"]
    prepopulated_fields = {"slug": ("nombre",)}
    ordering = ["nombre"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo", "creado"]
    list_filter = ["activo"]
    search_fields = ["nombre"]
    ordering = ["nombre"]


@admin.register(TipoLente)
class TipoLenteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "precio_adicional", "activo", "creado"]
    list_filter = ["activo"]
    search_fields = ["nombre"]
    ordering = ["nombre"]


@admin.register(Anteojo)
class AnteojoAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "sku",
        "marca",
        "categoria",
        "material",
        "precio",
        "stock",
        "activo",
        "destacado",
        "vista_miniatura",
    ]
    list_filter = [
        "activo",
        "destacado",
        "marca",
        "categoria",
        "material",
        "forma",
        "genero",
    ]
    search_fields = ["nombre", "sku", "marca__nombre", "color_marco"]
    filter_horizontal = ["tipos_lente"]
    inlines = [ImagenAnteojoInline]
    ordering = ["-creado"]

    def vista_miniatura(self, obj):
        primera = obj.imagenes.first()
        if primera and primera.imagen:
            return format_html(
                '<img src="{}" style="height: 40px; border-radius: 4px; object-fit: contain;" />',
                primera.imagen.url,
            )
        return "-"
    vista_miniatura.short_description = "Miniatura"


@admin.register(ImagenAnteojo)
class ImagenAnteojoAdmin(admin.ModelAdmin):
    list_display = ["anteojo", "es_modelo", "orden", "creado", "vista_previa"]
    list_filter = ["es_modelo", "anteojo__marca", "anteojo__categoria"]
    search_fields = ["anteojo__nombre", "anteojo__sku"]
    ordering = ["anteojo", "orden"]

    def vista_previa(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="height: 40px; border-radius: 4px;" />',
                obj.imagen.url,
            )
        return "-"
    vista_previa.short_description = "Vista previa"
