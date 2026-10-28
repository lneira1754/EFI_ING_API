from django.db import transaction
from rest_framework import serializers

from catalogo.models import Anteojo, TipoLente
from catalogo.serializers import AnteojoSimpleSerializer, TipoLenteSerializer
from clientes.serializers import ClienteSimpleSerializer
from .models import DetallePedido, Pedido, Resena


class DetallePedidoItemInputSerializer(serializers.Serializer):
    anteojo_id = serializers.IntegerField()
    tipo_lente_id = serializers.IntegerField(required=False, allow_null=True)
    cantidad = serializers.IntegerField(min_value=1, default=1)


class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = [
            "id",
            "pedido",
            "anteojo",
            "tipo_lente",
            "cantidad",
            "precio_unitario",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal", "precio_unitario"]


class DetallePedidoNestedSerializer(serializers.ModelSerializer):
    anteojo = AnteojoSimpleSerializer(read_only=True)
    tipo_lente = TipoLenteSerializer(read_only=True)

    class Meta:
        model = DetallePedido
        fields = [
            "id",
            "anteojo",
            "tipo_lente",
            "cantidad",
            "precio_unitario",
            "subtotal",
        ]


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer para crear y consultar pedidos individuales de forma plana."""
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    items = DetallePedidoItemInputSerializer(
        many=True,
        write_only=True,
        required=False,
        help_text="Lista de productos a incluir en el pedido",
    )

    class Meta:
        model = Pedido
        fields = [
            "id",
            "cliente",
            "receta",
            "estado",
            "total",
            "notas",
            "items",
            "detalles",
            "creado",
            "actualizado",
        ]
        read_only_fields = ["id", "total", "estado", "creado", "actualizado"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        with transaction.atomic():
            pedido = Pedido.objects.create(**validated_data)
            total = 0
            for item in items_data:
                anteojo = Anteojo.objects.get(id=item["anteojo_id"])
                tipo_lente = None
                tipo_id = item.get("tipo_lente_id")
                if tipo_id:
                    tipo_lente = TipoLente.objects.get(id=tipo_id)
                detalle = DetallePedido.objects.create(
                    pedido=pedido,
                    anteojo=anteojo,
                    tipo_lente=tipo_lente,
                    cantidad=item.get("cantidad", 1),
                )
                total += detalle.subtotal
            pedido.total = total
            pedido.save(update_fields=["total"])
        return pedido


class PedidoListSerializer(serializers.ModelSerializer):
    """Serializer anidado utilizado unicamente en la accion list (get all)."""
    cliente = ClienteSimpleSerializer(read_only=True)
    detalles = DetallePedidoNestedSerializer(many=True, read_only=True)
    cantidad_items = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = [
            "id",
            "cliente",
            "receta",
            "estado",
            "total",
            "cantidad_items",
            "detalles",
            "notas",
            "creado",
        ]
        read_only_fields = ["id", "total", "creado"]

    def get_cantidad_items(self, obj):
        return sum(d.cantidad for d in obj.detalles.all())


class ResenaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    anteojo_nombre = serializers.CharField(source="anteojo.nombre", read_only=True)

    class Meta:
        model = Resena
        fields = [
            "id",
            "cliente",
            "cliente_nombre",
            "anteojo",
            "anteojo_nombre",
            "puntaje",
            "comentario",
            "creado",
        ]
        read_only_fields = ["id", "cliente", "creado"]

    def get_cliente_nombre(self, obj):
        return obj.cliente.usuario.get_full_name() or obj.cliente.usuario.username

    def validate(self, attrs):
        # El cliente no viene en el body: es el usuario logueado (o el dueño, si se edita)
        request = self.context.get("request")
        if self.instance:
            cliente = self.instance.cliente
        else:
            cliente = getattr(request.user, "cliente", None) if request else None
        anteojo = attrs.get("anteojo", getattr(self.instance, "anteojo", None))

        if cliente and anteojo:
            existentes = Resena.objects.filter(cliente=cliente, anteojo=anteojo)
            if self.instance:
                existentes = existentes.exclude(pk=self.instance.pk)
            if existentes.exists():
                raise serializers.ValidationError(
                    {"anteojo": "Ya escribiste una reseña para este anteojo."}
                )
        return attrs