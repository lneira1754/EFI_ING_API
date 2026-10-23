from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalogo.models import Anteojo
from core.permissions import EsDuenioOAdmin, EsDuenioResenaOAdmin
from .models import Pedido, Resena
from .serializers import (
    PedidoListSerializer,
    PedidoSerializer,
    ResenaSerializer,
)


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = (
        Pedido.objects.select_related("cliente__usuario", "receta")
        .prefetch_related(
            "detalles__anteojo__imagenes",
            "detalles__tipo_lente",
        )
        .all()
    )
    permission_classes = [EsDuenioOAdmin]
    ordering_fields = ["creado", "total"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Pedido.objects.none()
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(cliente__usuario=user)

    def get_serializer_class(self):
        # Muestra datos anidados unicamente si se consulta un list (get all)
        if self.action == "list":
            return PedidoListSerializer
        return PedidoSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_staff and hasattr(user, "cliente"):
            serializer.save(cliente=user.cliente)
        else:
            serializer.save()

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        """Confirma el pedido, valida stock disponible y descuenta inventario."""
        pedido = self.get_object()
        if pedido.estado in [Pedido.Estado.PAGADO, Pedido.Estado.ENVIADO, Pedido.Estado.ENTREGADO]:
            return Response(
                {"detail": "El pedido ya se encuentra confirmado o pagado"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if pedido.estado == Pedido.Estado.CANCELADO:
            return Response(
                {"detail": "No se puede confirmar un pedido cancelado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            detalles = pedido.detalles.select_related("anteojo").all()
            if not detalles.exists():
                return Response(
                    {"detail": "El pedido no contiene productos para confirmar"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validar stock suficiente
            for det in detalles:
                anteojo = Anteojo.objects.select_for_update().get(id=det.anteojo_id)
                if anteojo.stock < det.cantidad:
                    return Response(
                        {
                            "detail": f"Stock insuficiente para el modelo '{anteojo.nombre}'. Disponible: {anteojo.stock}, solicitado: {det.cantidad}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Descontar stock
            for det in detalles:
                anteojo = Anteojo.objects.select_for_update().get(id=det.anteojo_id)
                anteojo.stock -= det.cantidad
                anteojo.save(update_fields=["stock"])

            pedido.estado = Pedido.Estado.PAGADO
            pedido.save(update_fields=["estado"])

        serializer = PedidoListSerializer(pedido, context={"request": request})
        return Response(
            {"detail": "Pedido confirmado exitosamente", "pedido": serializer.data}
        )

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Cancela el pedido y restituye el stock si habia sido confirmado."""
        pedido = self.get_object()
        if pedido.estado == Pedido.Estado.CANCELADO:
            return Response(
                {"detail": "El pedido ya esta cancelado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if pedido.estado == Pedido.Estado.PAGADO:
                for det in pedido.detalles.select_related("anteojo").all():
                    anteojo = Anteojo.objects.select_for_update().get(id=det.anteojo_id)
                    anteojo.stock += det.cantidad
                    anteojo.save(update_fields=["stock"])

            pedido.estado = Pedido.Estado.CANCELADO
            pedido.save(update_fields=["estado"])

        serializer = PedidoListSerializer(pedido, context={"request": request})
        return Response(
            {"detail": "Pedido cancelado correctamente", "pedido": serializer.data}
        )


class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.select_related("cliente__usuario", "anteojo").all()
    serializer_class = ResenaSerializer
    permission_classes = [EsDuenioResenaOAdmin]
    ordering_fields = ["creado", "puntaje"]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "cliente"):
            from clientes.models import Cliente
            # Crear perfil de cliente si no existe
            cliente, _ = Cliente.objects.get_or_create(
                usuario=user,
                defaults={"dni": f"USR-{user.id}"},
            )
            serializer.save(cliente=cliente)
        else:
            serializer.save(cliente=user.cliente)
