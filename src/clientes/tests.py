from datetime import date

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, Optometrista, Receta, Turno


class ClientesBaseTestCase(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("pepe", password="1234")
        self.cliente = Cliente.objects.create(usuario=self.usuario, dni="30111222", telefono="3511234567")
        self.otro_usuario = User.objects.create_user("juana", password="1234")
        self.otro_cliente = Cliente.objects.create(usuario=self.otro_usuario, dni="30999888")
        self.optometrista = Optometrista.objects.create(nombre="Laura", apellido="Gomez", matricula="MP-100")


class ClientePerfilTests(ClientesBaseTestCase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_superuser("admin", password="admin1234")
        self.url = "/api/clientes/me/"

    def test_me_sin_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_con_cliente(self):
        self.client.login(username="pepe", password="1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["dni"], "30111222")
        self.assertEqual(response.data["username"], "pepe")

    def test_me_usuario_sin_cliente(self):
        self.client.login(username="admin", password="admin1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_me_actualizar_perfil(self):
        self.client.login(username="pepe", password="1234")
        response = self.client.patch(self.url, {"telefono": "3519999999", "direccion": "San Martin 123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.telefono, "3519999999")
        self.assertEqual(self.cliente.direccion, "San Martin 123")


class PrivacidadClienteTests(ClientesBaseTestCase):
    def setUp(self):
        super().setUp()
        ahora = timezone.now()
        self.turno_propio = Turno.objects.create(cliente=self.cliente, optometrista=self.optometrista, fecha_hora=ahora)
        self.turno_ajeno = Turno.objects.create(cliente=self.otro_cliente, optometrista=self.optometrista, fecha_hora=ahora)
        self.receta_propia = Receta.objects.create(cliente=self.cliente, optometrista=self.optometrista, fecha_emision=date.today())
        self.receta_ajena = Receta.objects.create(cliente=self.otro_cliente, optometrista=self.optometrista, fecha_emision=date.today())

    def test_list_turnos_solo_propios(self):
        self.client.login(username="pepe", password="1234")
        response = self.client.get("/api/turnos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [t["id"] for t in response.data["results"]]
        self.assertEqual(ids, [self.turno_propio.id])

    def test_detalle_turno_ajeno(self):
        self.client.login(username="pepe", password="1234")
        response = self.client.get(f"/api/turnos/{self.turno_ajeno.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_recetas_solo_propias(self):
        self.client.login(username="pepe", password="1234")
        response = self.client.get("/api/recetas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [r["id"] for r in response.data["results"]]
        self.assertEqual(ids, [self.receta_propia.id])

    def test_list_turnos_sin_auth(self):
        response = self.client.get("/api/turnos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TurnoTests(ClientesBaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/api/turnos/"
        self.client.login(username="pepe", password="1234")

    def test_create_turno_asigna_cliente_logueado(self):
        # Aunque se envie otro cliente, perform_create asigna el del usuario logueado
        data = {
            "cliente": self.otro_cliente.id,
            "optometrista": self.optometrista.id,
            "fecha_hora": "2026-12-01T10:00:00Z",
            "motivo": "Control anual",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        turno = Turno.objects.get(id=response.data["id"])
        self.assertEqual(turno.cliente, self.cliente)
        self.assertEqual(turno.estado, Turno.Estado.PENDIENTE)

    def test_cancelar_turno(self):
        turno = Turno.objects.create(cliente=self.cliente, optometrista=self.optometrista, fecha_hora=timezone.now())
        response = self.client.post(f"{self.url}{turno.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["turno"]["estado"], Turno.Estado.CANCELADO)
        turno.refresh_from_db()
        self.assertEqual(turno.estado, Turno.Estado.CANCELADO)

    def test_cancelar_turno_dos_veces(self):
        turno = Turno.objects.create(cliente=self.cliente, optometrista=self.optometrista, fecha_hora=timezone.now())
        self.client.post(f"{self.url}{turno.id}/cancelar/")
        response = self.client.post(f"{self.url}{turno.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
