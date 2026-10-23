from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Cliente, Optometrista, Receta, Turno


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]
        read_only_fields = ["id", "username"]


class OptometristaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Optometrista
        fields = [
            "id",
            "nombre",
            "apellido",
            "matricula",
            "email",
            "telefono",
            "especialidad",
            "activo",
            "creado",
        ]
        read_only_fields = ["id", "creado"]


class ClienteSimpleSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ["id", "dni", "telefono", "nombre_completo"]

    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username


class ClienteSerializer(serializers.ModelSerializer):
    usuario = UserSimpleSerializer(read_only=True)
    nombre = serializers.CharField(source="usuario.first_name", read_only=True)
    apellido = serializers.CharField(source="usuario.last_name", read_only=True)
    email = serializers.EmailField(source="usuario.email", read_only=True)
    username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "id",
            "usuario",
            "username",
            "nombre",
            "apellido",
            "email",
            "dni",
            "telefono",
            "direccion",
            "fecha_nacimiento",
            "creado",
        ]
        read_only_fields = ["id", "creado", "usuario"]


class RecetaSerializer(serializers.ModelSerializer):
    optometrista_detalle = OptometristaSerializer(source="optometrista", read_only=True)

    class Meta:
        model = Receta
        fields = [
            "id",
            "cliente",
            "optometrista",
            "optometrista_detalle",
            "fecha_emision",
            "od_esfera",
            "od_cilindro",
            "od_eje",
            "oi_esfera",
            "oi_cilindro",
            "oi_eje",
            "adicion",
            "distancia_pupilar",
            "observaciones",
            "creado",
        ]
        read_only_fields = ["id", "creado"]


class TurnoSerializer(serializers.ModelSerializer):
    optometrista_detalle = OptometristaSerializer(source="optometrista", read_only=True)
    cliente_detalle = ClienteSimpleSerializer(source="cliente", read_only=True)

    class Meta:
        model = Turno
        fields = [
            "id",
            "cliente",
            "cliente_detalle",
            "optometrista",
            "optometrista_detalle",
            "fecha_hora",
            "motivo",
            "estado",
            "notas",
            "creado",
        ]
        read_only_fields = ["id", "creado"]
