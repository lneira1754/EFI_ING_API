from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente
from ventas.models import Resena
from .models import Anteojo, Categoria, Marca, Material


def crear_catalogo_base():
    marca = Marca.objects.create(nombre="Ray-Ban", pais_origen="Italia")
    categoria = Categoria.objects.create(nombre="Sol", slug="sol")
    material = Material.objects.create(nombre="Acetato")
    return marca, categoria, material


def crear_anteojo(marca, categoria, material, **kwargs):
    datos = {
        "nombre": "Wayfarer Classic",
        "sku": "RB-001",
        "marca": marca,
        "categoria": categoria,
        "material": material,
        "color_marco": "Negro",
        "precio": 100000,
        "stock": 10,
    }
    datos.update(kwargs)
    return Anteojo.objects.create(**datos)


class AutenticacionJWTTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("pepe", password="1234")
        self.url = "/api/token/"

    def test_login_jwt_credenciales_validas(self):
        response = self.client.post(self.url, {"username": "pepe", "password": "1234"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_jwt_credenciales_invalidas(self):
        response = self.client.post(self.url, {"username": "pepe", "password": "incorrecta"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_acceso_con_token_jwt(self):
        # El token obtenido sirve para endpoints protegidos
        response = self.client.post(self.url, {"username": "pepe", "password": "1234"})
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/turnos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AnteojoPermisosTests(APITestCase):
    def setUp(self):
        self.marca, self.categoria, self.material = crear_catalogo_base()
        self.usuario = User.objects.create_user("pepe", password="1234")
        self.admin = User.objects.create_superuser("admin", password="admin1234")
        self.anteojo = crear_anteojo(self.marca, self.categoria, self.material)
        self.url = "/api/anteojos/"
        self.data = {
            "nombre": "Aviador Gold",
            "sku": "RB-002",
            "marca": self.marca.id,
            "categoria": self.categoria.id,
            "material": self.material.id,
            "color_marco": "Dorado",
            "precio": "150000.00",
            "stock": 5,
        }

    def test_list_anteojos_sin_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_anteojo_sin_auth(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_anteojo_usuario_comun(self):
        self.client.login(username="pepe", password="1234")
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Anteojo.objects.count(), 1)

    def test_create_anteojo_con_admin(self):
        self.client.login(username="admin", password="admin1234")
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Anteojo.objects.count(), 2)
        self.assertEqual(response.data["sku"], "RB-002")


class AnteojoFiltrosTests(APITestCase):
    def setUp(self):
        marca, categoria, material = crear_catalogo_base()
        self.barato = crear_anteojo(marca, categoria, material, nombre="Redondo Basico", sku="A-1", precio=50000, stock=0)
        self.medio = crear_anteojo(marca, categoria, material, nombre="Aviador Plata", sku="A-2", precio=120000, stock=3, destacado=True)
        self.caro = crear_anteojo(marca, categoria, material, nombre="Cat Eye Lujo", sku="A-3", precio=300000, stock=7)
        self.url = "/api/anteojos/"

    def ids(self, response):
        return {item["id"] for item in response.data["results"]}

    def test_filtrar_por_rango_de_precio(self):
        response = self.client.get(self.url, {"precio_min": 100000, "precio_max": 200000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.ids(response), {self.medio.id})

    def test_filtrar_en_stock(self):
        response = self.client.get(self.url, {"en_stock": "true"})
        self.assertEqual(self.ids(response), {self.medio.id, self.caro.id})
        response = self.client.get(self.url, {"en_stock": "false"})
        self.assertEqual(self.ids(response), {self.barato.id})

    def test_buscar_por_nombre(self):
        response = self.client.get(self.url, {"search": "aviador"})
        self.assertEqual(self.ids(response), {self.medio.id})

    def test_destacados_solo_devuelve_destacados(self):
        response = self.client.get(self.url + "destacados/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.ids(response), {self.medio.id})


class AnteojoResenasTests(APITestCase):
    def setUp(self):
        marca, categoria, material = crear_catalogo_base()
        self.anteojo = crear_anteojo(marca, categoria, material)
        self.otro = crear_anteojo(marca, categoria, material, sku="RB-999")
        usuario = User.objects.create_user("pepe", password="1234")
        cliente = Cliente.objects.create(usuario=usuario, dni="30111222")
        Resena.objects.create(cliente=cliente, anteojo=self.anteojo, puntaje=5, comentario="Excelente")
        Resena.objects.create(cliente=cliente, anteojo=self.otro, puntaje=2)
        self.url = f"/api/anteojos/{self.anteojo.id}/resenas/"

    def test_resenas_de_un_anteojo(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["anteojo"], self.anteojo.id)
        self.assertEqual(response.data[0]["puntaje"], 5)
