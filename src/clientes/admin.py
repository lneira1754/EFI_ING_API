from django.contrib import admin
from .models import Cliente, Optometrista, Receta, Turno


class RecetaInline(admin.StackedInline):
    model = Receta
    extra = 0
    fields = [
        "fecha_emision",
        "optometrista",
        ("od_esfera", "od_cilindro", "od_eje"),
        ("oi_esfera", "oi_cilindro", "oi_eje"),
        ("adicion", "distancia_pupilar"),
        "observaciones",
    ]


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        "usuario",
        "dni",
        "telefono",
        "direccion",
        "fecha_nacimiento",
        "creado",
    ]
    list_filter = ["creado"]
    search_fields = [
        "dni",
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "telefono",
    ]
    inlines = [RecetaInline]
    ordering = ["-creado"]


@admin.register(Optometrista)
class OptometristaAdmin(admin.ModelAdmin):
    list_display = [
        "apellido",
        "nombre",
        "matricula",
        "especialidad",
        "telefono",
        "activo",
    ]
    list_filter = ["activo", "especialidad"]
    search_fields = ["apellido", "nombre", "matricula"]
    ordering = ["apellido", "nombre"]


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "optometrista",
        "fecha_emision",
        "od_esfera",
        "oi_esfera",
        "distancia_pupilar",
        "creado",
    ]
    list_filter = ["fecha_emision", "optometrista"]
    search_fields = [
        "cliente__dni",
        "cliente__usuario__username",
        "cliente__usuario__first_name",
        "cliente__usuario__last_name",
    ]
    ordering = ["-fecha_emision", "-id"]


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "optometrista",
        "fecha_hora",
        "motivo",
        "estado",
        "creado",
    ]
    list_filter = ["estado", "fecha_hora", "optometrista"]
    search_fields = [
        "cliente__dni",
        "cliente__usuario__username",
        "optometrista__apellido",
        "motivo",
    ]
    ordering = ["-fecha_hora"]
