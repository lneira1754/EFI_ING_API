from django.views.generic import TemplateView
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
