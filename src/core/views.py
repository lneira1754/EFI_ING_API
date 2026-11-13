from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from catalogo.models import Anteojo, Categoria, Marca


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Productos destacados o primeros productos activos para la portada
        context["anteojos"] = (
            Anteojo.objects.filter(activo=True)
            .select_related("marca", "categoria")
            .prefetch_related("imagenes")[:6]
        )
        context["total_anteojos"] = Anteojo.objects.filter(activo=True).count()
        context["marcas"] = Marca.objects.filter(activo=True)
        context["categorias"] = Categoria.objects.filter(activo=True)
        context["endpoints_count"] = 12
        return context


class UsuarioActualView(APIView):
    """Datos del usuario autenticado, tenga o no perfil de cliente."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        usuario = request.user
        cliente = getattr(usuario, "cliente", None)
        return Response(
            {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "nombre": usuario.first_name,
                "apellido": usuario.last_name,
                "is_staff": usuario.is_staff,
                "cliente_id": cliente.id if cliente else None,
            }
        )
