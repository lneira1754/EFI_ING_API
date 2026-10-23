from django.contrib import admin
from .models import DetallePedido, Pedido, Resena


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    fields = ["anteojo", "tipo_lente", "cantidad", "precio_unitario", "subtotal"]
    readonly_fields = ["subtotal"]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "estado",
        "total",
        "receta",
        "creado",
        "actualizado",
    ]
    list_filter = ["estado", "creado", "actualizado"]
    search_fields = [
        "cliente__dni",
        "cliente__usuario__username",
        "cliente__usuario__first_name",
        "cliente__usuario__last_name",
    ]
    inlines = [DetallePedidoInline]
    readonly_fields = ["total"]
    ordering = ["-creado"]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "pedido",
        "anteojo",
        "tipo_lente",
        "cantidad",
        "precio_unitario",
        "subtotal",
    ]
    list_filter = ["anteojo__marca", "tipo_lente"]
    search_fields = ["pedido__id", "anteojo__nombre"]
    ordering = ["-pedido__id"]


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "anteojo", "puntaje", "creado"]
    list_filter = ["puntaje", "creado", "anteojo__marca"]
    search_fields = [
        "cliente__dni",
        "cliente__usuario__username",
        "anteojo__nombre",
        "comentario",
    ]
    ordering = ["-creado"]
