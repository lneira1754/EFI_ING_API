from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, OptometristaViewSet, RecetaViewSet, TurnoViewSet

router = DefaultRouter()
router.register(r"optometristas", OptometristaViewSet, basename="optometrista")
router.register(r"clientes", ClienteViewSet, basename="cliente")
router.register(r"recetas", RecetaViewSet, basename="receta")
router.register(r"turnos", TurnoViewSet, basename="turno")

urlpatterns = router.urls
