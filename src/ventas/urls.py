from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, ResenaViewSet

router = DefaultRouter()
router.register(r"pedidos", PedidoViewSet, basename="pedido")
router.register(r"resenas", ResenaViewSet, basename="resena")

urlpatterns = router.urls
