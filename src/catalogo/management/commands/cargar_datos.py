import os
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalogo.models import (
    Anteojo,
    Categoria,
    ImagenAnteojo,
    Marca,
    Material,
    TipoLente,
)
from clientes.models import Cliente, Optometrista, Receta, Turno
from ventas.models import DetallePedido, Pedido, Resena


class Command(BaseCommand):
    help = "Carga datos iniciales de prueba y asocia imagenes de anteojos"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando carga de datos iniciales..."))

        # 1. Marcas
        marcas_data = [
            ("Ray-Ban", "Italia", "Marca de diseno y calidad optica"),
            ("Hawkers", "Espana", "Estilo urbano y proteccion UV"),
            ("Vision Pro", "Argentina", "Especialistas en luz azul y descanso visual"),
            ("Oakley", "Estados Unidos", "Rendimiento y resistencia deportiva"),
        ]
        marcas = {}
        for nombre, pais, desc in marcas_data:
            m, _ = Marca.objects.get_or_create(
                nombre=nombre,
                defaults={"pais_origen": pais, "descripcion": desc, "activo": True},
            )
            marcas[nombre] = m

        # 2. Categorias
        cat_data = [
            ("Luz Azul", "luz-azul", "Anteojos con filtro especial para pantallas y descanso"),
            ("Sol", "sol", "Lentes polarizados con proteccion contra rayos UV"),
            ("Recetados", "recetados", "Armazones listos para graduacion oftalmica"),
        ]
        categorias = {}
        for nombre, slug, desc in cat_data:
            c, _ = Categoria.objects.get_or_create(
                slug=slug,
                defaults={"nombre": nombre, "descripcion": desc, "activo": True},
            )
            categorias[slug] = c

        # 3. Materiales
        mat_data = [
            ("Acetato", "Acetato de celulosa premium hipoalergenico"),
            ("Metal", "Aleacion metalica liviana con acabado resistente"),
            ("TR90", "Polimero con memoria termoplastica ultraliviano"),
        ]
        materiales = {}
        for nombre, desc in mat_data:
            mat, _ = Material.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": desc, "activo": True},
            )
            materiales[nombre] = mat

        # 4. Tipos de Lente
        lentes_data = [
            ("Monofocal Antirreflejo", "Correccion para una sola distancia con filtro antireflejo", Decimal("4500.00")),
            ("Filtro Luz Azul BlueBlocker", "Bloqueo selectivo de luz azul nociva de dispositivos", Decimal("6200.00")),
            ("Multifocal Progresivo", "Transicion suave para vision cercana, intermedia y lejana", Decimal("12800.00")),
            ("Polarizado PolarPro", "Eliminacion de reflejos y maximo contraste solar", Decimal("5500.00")),
        ]
        tipos_lente = {}
        for nombre, desc, precio_add in lentes_data:
            tl, _ = TipoLente.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": desc, "precio_adicional": precio_add, "activo": True},
            )
            tipos_lente[nombre] = tl

        # 5. Modelos de Anteojos e Imagenes
        directorio_imagenes = os.path.join(settings.BASE_DIR.parent, "img_anteojos")

        modelos_config = [
            {
                "nombre": "Cooper Luz Azul con Antirreflejo",
                "sku": "ANT-COOPER-01",
                "marca": marcas["Vision Pro"],
                "categoria": categorias["luz-azul"],
                "material": materiales["Acetato"],
                "forma": Anteojo.Forma.WAYFARER,
                "genero": Anteojo.Genero.UNISEX,
                "color_marco": "Carey Clasico",
                "color_lente": "Transparente AR",
                "precio": Decimal("24500.00"),
                "stock": 15,
                "destacado": True,
                "descripcion": "Diseno moderno para uso prolongado frente a monitores.",
                "img_prod": "Anteojos_Filtro_Luz_Azul_Cooper_con_Antireflejo.webp",
                "img_mod": "Anteojos_Filtro_Luz_Azul_Cooper_con_Antireflejo_Modelo.webp",
            },
            {
                "nombre": "Don Juan Luz Azul con Antirreflejo",
                "sku": "ANT-DONJUAN-02",
                "marca": marcas["Vision Pro"],
                "categoria": categorias["luz-azul"],
                "material": materiales["Acetato"],
                "forma": Anteojo.Forma.RECTANGULAR,
                "genero": Anteojo.Genero.HOMBRE,
                "color_marco": "Negro Mate",
                "color_lente": "Transparente AR",
                "precio": Decimal("26800.00"),
                "stock": 10,
                "destacado": True,
                "descripcion": "Estructura rectangular resistente y elegante.",
                "img_prod": "Anteojos_Filtro_Luz_Azul_Don_Juan_con_Antireflejo.webp",
                "img_mod": "Anteojos_Filtro_Luz_Azul_Don_Juan_con_Antireflejo_Modelo.webp",
            },
            {
                "nombre": "Maryland Luz Azul con Antirreflejo",
                "sku": "ANT-MARYLAND-03",
                "marca": marcas["Hawkers"],
                "categoria": categorias["luz-azul"],
                "material": materiales["Metal"],
                "forma": Anteojo.Forma.REDONDO,
                "genero": Anteojo.Genero.UNISEX,
                "color_marco": "Dorado Satinado",
                "color_lente": "Transparente AR",
                "precio": Decimal("29500.00"),
                "stock": 12,
                "destacado": True,
                "descripcion": "Marco fino metalico de inspiracion vintage.",
                "img_prod": "Anteojos_Filtro_Luz_Azul_Maryland_con_Antireflejo.webp",
                "img_mod": "Anteojos_Filtro_Luz_Azul_Maryland_con_Antireflejo_Modelo.webp",
            },
            {
                "nombre": "Brooklyn Carey Lente Negro",
                "sku": "ANT-BROOKLYN-04",
                "marca": marcas["Ray-Ban"],
                "categoria": categorias["sol"],
                "material": materiales["Acetato"],
                "forma": Anteojo.Forma.WAYFARER,
                "genero": Anteojo.Genero.UNISEX,
                "color_marco": "Carey Habana",
                "color_lente": "Negro Polarizado",
                "precio": Decimal("38900.00"),
                "stock": 8,
                "destacado": True,
                "descripcion": "Lentes de sol iconicos con proteccion UV400 total.",
                "img_prod": "Brooklyn_Carey_Lente_Negro.webp",
                "img_mod": "Brooklyn_Carey_Lente_Negro_Modelo.webp",
            },
            {
                "nombre": "Melbourne Carey Lente Marron",
                "sku": "ANT-MELBOURNE-05",
                "marca": marcas["Hawkers"],
                "categoria": categorias["sol"],
                "material": materiales["TR90"],
                "forma": Anteojo.Forma.CAT_EYE,
                "genero": Anteojo.Genero.MUJER,
                "color_marco": "Carey Ambar",
                "color_lente": "Marron Degradé",
                "precio": Decimal("32400.00"),
                "stock": 14,
                "destacado": False,
                "descripcion": "Silueta femenina audaz con cristales en degrade.",
                "img_prod": "Melbourne_Carey_Lente_Marron.webp",
                "img_mod": "Melbourne_Carey_Lente_Marron_Modelo.webp",
            },
            {
                "nombre": "Moonshine Lente Negro",
                "sku": "ANT-MOONSHINE-06",
                "marca": marcas["Oakley"],
                "categoria": categorias["sol"],
                "material": materiales["TR90"],
                "forma": Anteojo.Forma.HEXAGONAL,
                "genero": Anteojo.Genero.HOMBRE,
                "color_marco": "Negro Onix",
                "color_lente": "Negro Humo",
                "precio": Decimal("35700.00"),
                "stock": 6,
                "destacado": True,
                "descripcion": "Estilo contemporaneo y lineas geometricas definidas.",
                "img_prod": "Moonshine_Lente_Negro.webp",
                "img_mod": "Moonshine_Lente_Negro_Modelo.webp",
            },
        ]

        for item in modelos_config:
            anteojo, created = Anteojo.objects.get_or_create(
                sku=item["sku"],
                defaults={
                    "nombre": item["nombre"],
                    "marca": item["marca"],
                    "categoria": item["categoria"],
                    "material": item["material"],
                    "forma": item["forma"],
                    "genero": item["genero"],
                    "color_marco": item["color_marco"],
                    "color_lente": item["color_lente"],
                    "precio": item["precio"],
                    "stock": item["stock"],
                    "destacado": item["destacado"],
                    "descripcion": item["descripcion"],
                    "activo": True,
                },
            )
            # Asignar tipos de lente compatibles
            anteojo.tipos_lente.set(tipos_lente.values())

            # Cargar imagen de producto
            if not anteojo.imagenes.filter(es_modelo=False).exists():
                ruta_prod = os.path.join(directorio_imagenes, item["img_prod"])
                if os.path.exists(ruta_prod):
                    with open(ruta_prod, "rb") as f:
                        img_obj = ImagenAnteojo(anteojo=anteojo, es_modelo=False, orden=1)
                        img_obj.imagen.save(item["img_prod"], File(f), save=True)

            # Cargar imagen con modelo posando
            if not anteojo.imagenes.filter(es_modelo=True).exists():
                ruta_mod = os.path.join(directorio_imagenes, item["img_mod"])
                if os.path.exists(ruta_mod):
                    with open(ruta_mod, "rb") as f:
                        img_obj = ImagenAnteojo(anteojo=anteojo, es_modelo=True, orden=2)
                        img_obj.imagen.save(item["img_mod"], File(f), save=True)

        # 6. Optometristas
        opt1, _ = Optometrista.objects.get_or_create(
            matricula="MN-48291",
            defaults={
                "nombre": "Sofia",
                "apellido": "Valenzuela",
                "email": "sofia.valenzuela@optica.com",
                "telefono": "+54 9 358 4123456",
                "especialidad": "Contactologia y refraccion avanzada",
                "activo": True,
            },
        )
        opt2, _ = Optometrista.objects.get_or_create(
            matricula="MN-51902",
            defaults={
                "nombre": "Martin",
                "apellido": "Benitez",
                "email": "martin.benitez@optica.com",
                "telefono": "+54 9 358 4987654",
                "especialidad": "Salud visual preventiva y control de miopia",
                "activo": True,
            },
        )

        # 7. Superusuario admin
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@optica.com", "admin1234")
            self.stdout.write(self.style.SUCCESS("Superusuario 'admin' creado (password: admin1234)"))

        # 8. Cliente demo
        user_demo, created_user = User.objects.get_or_create(
            username="cliente_demo",
            defaults={
                "first_name": "Agustin",
                "last_name": "Gomez",
                "email": "agustin.gomez@gmail.com",
            },
        )
        if created_user:
            user_demo.set_password("demo1234")
            user_demo.save()

        cliente_demo, _ = Cliente.objects.get_or_create(
            usuario=user_demo,
            defaults={
                "dni": "39485120",
                "telefono": "+54 9 358 5551234",
                "direccion": "Av. San Martin 450, Rio Cuarto",
            },
        )

        # 9. Receta de prueba
        receta_demo, _ = Receta.objects.get_or_create(
            cliente=cliente_demo,
            fecha_emision=timezone.now().date(),
            defaults={
                "optometrista": opt1,
                "od_esfera": Decimal("-1.25"),
                "od_cilindro": Decimal("-0.50"),
                "od_eje": 85,
                "oi_esfera": Decimal("-1.00"),
                "oi_cilindro": Decimal("-0.75"),
                "oi_eje": 90,
                "adicion": Decimal("0.00"),
                "distancia_pupilar": Decimal("62.5"),
                "observaciones": "Control visual anual sin patologias. Apto para filtro BlueBlocker.",
            },
        )

        # 10. Turno de prueba
        Turno.objects.get_or_create(
            cliente=cliente_demo,
            optometrista=opt1,
            fecha_hora=timezone.now() + timezone.timedelta(days=3, hours=4),
            defaults={
                "motivo": "Revisión anual y renovacion de cristales",
                "estado": Turno.Estado.CONFIRMADO,
                "notas": "Traer anteojos actuales a la consulta.",
            },
        )

        # 11. Pedido de prueba
        primer_anteojo = Anteojo.objects.first()
        segundo_anteojo = Anteojo.objects.last()
        lente_blue = tipos_lente.get("Filtro Luz Azul BlueBlocker")

        pedido, created_pedido = Pedido.objects.get_or_create(
            cliente=cliente_demo,
            receta=receta_demo,
            defaults={
                "estado": Pedido.Estado.PAGADO,
                "total": Decimal("0.00"),
                "notas": "Envio a domicilio en horario matutino.",
            },
        )
        if created_pedido and primer_anteojo:
            DetallePedido.objects.create(
                pedido=pedido,
                anteojo=primer_anteojo,
                tipo_lente=lente_blue,
                cantidad=1,
            )
            if segundo_anteojo and segundo_anteojo != primer_anteojo:
                DetallePedido.objects.create(
                    pedido=pedido,
                    anteojo=segundo_anteojo,
                    tipo_lente=None,
                    cantidad=1,
                )
            pedido.calcular_total()
            pedido.save()

        # 12. Resena de prueba
        if primer_anteojo:
            Resena.objects.get_or_create(
                cliente=cliente_demo,
                anteojo=primer_anteojo,
                defaults={
                    "puntaje": 5,
                    "comentario": "Excelente calidad de los armazones y nitidez del filtro de luz azul. Muy comodos para trabajar todo el dia.",
                },
            )

        self.stdout.write(self.style.SUCCESS("Carga de datos de prueba completada exitosamente."))
