from rest_framework import serializers
from .models import Anteojo, Categoria, ImagenAnteojo, Marca, Material, TipoLente


class MarcaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "pais_origen"]


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "pais_origen", "descripcion", "activo", "creado"]
        read_only_fields = ["id", "creado"]


class CategoriaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug"]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug", "descripcion", "activo", "creado"]
        read_only_fields = ["id", "creado"]


class MaterialSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "nombre"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "nombre", "descripcion", "activo", "creado"]
        read_only_fields = ["id", "creado"]


class TipoLenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoLente
        fields = ["id", "nombre", "descripcion", "precio_adicional", "activo", "creado"]
        read_only_fields = ["id", "creado"]


class ImagenAnteojoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenAnteojo
        fields = ["id", "anteojo", "imagen", "es_modelo", "orden", "creado"]
        read_only_fields = ["id", "creado"]


class ImagenAnteojoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenAnteojo
        fields = ["id", "imagen", "es_modelo", "orden"]


class AnteojoSimpleSerializer(serializers.ModelSerializer):
    """Serializer basico para anidar en otros modelos."""
    imagen_principal = serializers.SerializerMethodField()

    class Meta:
        model = Anteojo
        fields = [
            "id",
            "nombre",
            "sku",
            "precio",
            "color_marco",
            "imagen_principal",
        ]

    def get_imagen_principal(self, obj):
        primera = obj.imagenes.filter(es_modelo=False).first() or obj.imagenes.first()
        if primera and primera.imagen:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(primera.imagen.url)
            return primera.imagen.url
        return None


class AnteojoSerializer(serializers.ModelSerializer):
    """Serializer plano para operaciones CRUD (crear/actualizar/detalle individual)."""

    class Meta:
        model = Anteojo
        fields = [
            "id",
            "nombre",
            "sku",
            "marca",
            "categoria",
            "material",
            "tipos_lente",
            "forma",
            "genero",
            "color_marco",
            "color_lente",
            "precio",
            "stock",
            "activo",
            "destacado",
            "descripcion",
            "creado",
            "actualizado",
        ]
        read_only_fields = ["id", "creado", "actualizado"]


class AnteojoListSerializer(serializers.ModelSerializer):
    """Serializer anidado utilizado unicamente en la accion list (get all)."""
    marca = MarcaSimpleSerializer(read_only=True)
    categoria = CategoriaSimpleSerializer(read_only=True)
    material = MaterialSimpleSerializer(read_only=True)
    tipos_lente = TipoLenteSerializer(many=True, read_only=True)
    imagenes = ImagenAnteojoSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Anteojo
        fields = [
            "id",
            "nombre",
            "sku",
            "marca",
            "categoria",
            "material",
            "tipos_lente",
            "forma",
            "genero",
            "color_marco",
            "color_lente",
            "precio",
            "stock",
            "activo",
            "destacado",
            "imagenes",
            "creado",
        ]
        read_only_fields = ["id", "creado"]
