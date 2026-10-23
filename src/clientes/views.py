from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import EsAdminOSoloLectura, EsDuenioOAdmin
from .models import Cliente, Optometrista, Receta, Turno
from .serializers import (
    ClienteSerializer,
    OptometristaSerializer,
    RecetaSerializer,
    TurnoSerializer,
)


class OptometristaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Optometrista.objects.filter(activo=True)
    serializer_class = OptometristaSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["nombre", "apellido", "matricula", "especialidad"]
    ordering_fields = ["apellido", "nombre"]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.select_related("usuario").all()
    serializer_class = ClienteSerializer
    permission_classes = [EsDuenioOAdmin]
    search_fields = ["dni", "usuario__first_name", "usuario__last_name", "telefono"]
    ordering_fields = ["creado", "usuario__last_name"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Cliente.objects.none()
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(usuario=user)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        """Retorna o actualiza el perfil del cliente actualmente autenticado."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "No autenticado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            cliente = request.user.cliente
        except Cliente.DoesNotExist:
            return Response(
                {"detail": "El usuario no tiene perfil de cliente asociado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "PATCH":
            serializer = self.get_serializer(cliente, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(cliente)
        return Response(serializer.data)


class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.select_related("cliente__usuario", "optometrista").all()
    serializer_class = RecetaSerializer
    permission_classes = [EsDuenioOAdmin]
    ordering_fields = ["fecha_emision", "creado"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Receta.objects.none()
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(cliente__usuario=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_staff and hasattr(user, "cliente"):
            serializer.save(cliente=user.cliente)
        else:
            serializer.save()


class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.select_related("cliente__usuario", "optometrista").all()
    serializer_class = TurnoSerializer
    permission_classes = [EsDuenioOAdmin]
    ordering_fields = ["fecha_hora", "creado"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Turno.objects.none()
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(cliente__usuario=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_staff and hasattr(user, "cliente"):
            serializer.save(cliente=user.cliente)
        else:
            serializer.save()

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Permite al cliente o administrador cancelar un turno programado."""
        turno = self.get_object()
        if turno.estado == Turno.Estado.CANCELADO:
            return Response(
                {"detail": "El turno ya se encuentra cancelado"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        turno.estado = Turno.Estado.CANCELADO
        turno.save()
        serializer = self.get_serializer(turno)
        return Response(
            {"detail": "Turno cancelado correctamente", "turno": serializer.data}
        )
