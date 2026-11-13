from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente


class UsuarioActualTests(APITestCase):
    url = "/api/usuarios/me/"

    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@optica.com", "admin1234")
        self.usuario = User.objects.create_user("pepe", password="1234", first_name="Pepe")
        self.cliente = Cliente.objects.create(usuario=self.usuario, dni="30111222")

    def test_sin_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_sin_perfil_de_cliente(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "admin")
        self.assertTrue(response.data["is_staff"])
        self.assertIsNone(response.data["cliente_id"])

    def test_cliente(self):
        self.client.force_authenticate(self.usuario)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "Pepe")
        self.assertFalse(response.data["is_staff"])
        self.assertEqual(response.data["cliente_id"], self.cliente.id)
