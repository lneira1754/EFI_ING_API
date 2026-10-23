from rest_framework.routers import DefaultRouter
from .views import (
    AnteojoViewSet,
    CategoriaViewSet,
    ImagenAnteojoViewSet,
    MarcaViewSet,
    MaterialViewSet,
    TipoLenteViewSet,
)

router = DefaultRouter()
router.register(r"marcas", MarcaViewSet, basename="marca")
router.register(r"categorias", CategoriaViewSet, basename="categoria")
router.register(r"materiales", MaterialViewSet, basename="material")
router.register(r"tipos-lente", TipoLenteViewSet, basename="tipo-lente")
router.register(r"anteojos", AnteojoViewSet, basename="anteojo")
router.register(r"imagenes-anteojo", ImagenAnteojoViewSet, basename="imagen-anteojo")

urlpatterns = router.urls
