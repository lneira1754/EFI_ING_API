from rest_framework.routers import DefaultRouter

from catalogo.views import (
    AnteojoViewSet,
    CategoriaViewSet,
    ImagenAnteojoViewSet,
    MarcaViewSet,
    MaterialViewSet,
    TipoLenteViewSet,
)
from clientes.views import (
    ClienteViewSet,
    OptometristaViewSet,
    RecetaViewSet,
    TurnoViewSet,
)
from ventas.views import PedidoViewSet, ResenaViewSet

api_router = DefaultRouter()

# Catalogo
api_router.register(r"marcas", MarcaViewSet, basename="marca")
api_router.register(r"categorias", CategoriaViewSet, basename="categoria")
api_router.register(r"materiales", MaterialViewSet, basename="material")
api_router.register(r"tipos-lente", TipoLenteViewSet, basename="tipo-lente")
api_router.register(r"anteojos", AnteojoViewSet, basename="anteojo")
api_router.register(r"imagenes-anteojo", ImagenAnteojoViewSet, basename="imagen-anteojo")

# Clientes y consultas
api_router.register(r"optometristas", OptometristaViewSet, basename="optometrista")
api_router.register(r"clientes", ClienteViewSet, basename="cliente")
api_router.register(r"recetas", RecetaViewSet, basename="receta")
api_router.register(r"turnos", TurnoViewSet, basename="turno")

# Ventas y pedidos
api_router.register(r"pedidos", PedidoViewSet, basename="pedido")
api_router.register(r"resenas", ResenaViewSet, basename="resena")
