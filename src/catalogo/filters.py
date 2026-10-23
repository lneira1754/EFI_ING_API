import django_filters
from .models import Anteojo, Categoria, Marca, Material


class AnteojoFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(
        field_name="precio",
        lookup_expr="gte",
        label="Precio mínimo",
    )
    precio_max = django_filters.NumberFilter(
        field_name="precio",
        lookup_expr="lte",
        label="Precio máximo",
    )
    marca = django_filters.ModelChoiceFilter(
        queryset=Marca.objects.all(),
        label="Marca",
    )
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.all(),
        label="Categoría",
    )
    material = django_filters.ModelChoiceFilter(
        queryset=Material.objects.all(),
        label="Material",
    )
    forma = django_filters.ChoiceFilter(
        choices=Anteojo.Forma.choices,
        label="Forma del marco",
    )
    genero = django_filters.ChoiceFilter(
        choices=Anteojo.Genero.choices,
        label="Género",
    )
    destacado = django_filters.BooleanFilter(
        field_name="destacado",
        label="Es producto destacado",
    )
    en_stock = django_filters.BooleanFilter(
        method="filter_en_stock",
        label="Tiene stock disponible",
    )

    class Meta:
        model = Anteojo
        fields = [
            "marca",
            "categoria",
            "material",
            "forma",
            "genero",
            "destacado",
            "precio_min",
            "precio_max",
            "en_stock",
        ]

    def filter_en_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(stock__gt=0)
        elif value is False:
            return queryset.filter(stock=0)
        return queryset
