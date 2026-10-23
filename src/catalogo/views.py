from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import EsAdminOSoloLectura
from .filters import AnteojoFilter
from .models import Anteojo, Categoria, ImagenAnteojo, Marca, Material, TipoLente
from .serializers import (
    AnteojoListSerializer,
    AnteojoSerializer,
    CategoriaSerializer,
    ImagenAnteojoSerializer,
    MarcaSerializer,
    MaterialSerializer,
    TipoLenteSerializer,
)


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [EsAdminOSoloLectura]
    filterset_fields = ["activo", "pais_origen"]
    search_fields = ["nombre", "pais_origen"]
    ordering_fields = ["nombre", "creado"]


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.filter(activo=True)
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    filterset_fields = ["activo"]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre"]


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.filter(activo=True)
    serializer_class = MaterialSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["activo"]
    search_fields = ["nombre"]
    ordering_fields = ["nombre"]


class TipoLenteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoLente.objects.filter(activo=True)
    serializer_class = TipoLenteSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["activo"]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "precio_adicional"]


class AnteojoViewSet(viewsets.ModelViewSet):
    queryset = (
        Anteojo.objects.select_related("marca", "categoria", "material")
        .prefetch_related("tipos_lente", "imagenes")
        .all()
    )
    permission_classes = [EsAdminOSoloLectura]
    filterset_class = AnteojoFilter
    search_fields = ["nombre", "sku", "marca__nombre", "color_marco"]
    ordering_fields = ["precio", "creado", "stock", "nombre"]

    def get_serializer_class(self):
        # Muestra datos anidados unicamente si se consulta un list (get all)
        if self.action == "list":
            return AnteojoListSerializer
        return AnteojoSerializer

    @action(detail=False, methods=["get"])
    def destacados(self, request):
        """Retorna anteojos marcados como destacados para portada."""
        queryset = self.get_queryset().filter(destacado=True, activo=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AnteojoListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = AnteojoListSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def resenas(self, request, pk=None):
        """Lista las resenas asociadas al anteojo."""
        anteojo = self.get_object()
        from ventas.serializers import ResenaSerializer

        resenas = anteojo.resenas.select_related("cliente__usuario").all()
        serializer = ResenaSerializer(resenas, many=True, context={"request": request})
        return Response(serializer.data)


class ImagenAnteojoViewSet(viewsets.ModelViewSet):
    queryset = ImagenAnteojo.objects.select_related("anteojo").all()
    serializer_class = ImagenAnteojoSerializer
    permission_classes = [EsAdminOSoloLectura]
    ordering_fields = ["orden", "id"]
