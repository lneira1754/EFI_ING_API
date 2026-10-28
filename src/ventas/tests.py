from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from catalogo.models import Anteojo, Categoria, Marca, Material, TipoLente
from clientes.models import Cliente
from .models import DetallePedido, Pedido, Resena


class VentasBaseTestCase(APITestCase):
    def setUp(self):
        marca = Marca.objects.create(nombre="Ray-Ban")
        categoria = Categoria.objects.create(nombre="Receta", slug="receta")
        material = Material.objects.create(nombre="Metal")
        self.anteojo = Anteojo.objects.create(
            nombre="Aviador", sku="RB-001", marca=marca, categoria=categoria,
            material=material, color_marco="Dorado", precio=Decimal("1000.00"), stock=5,
        )
        self.anteojo2 = Anteojo.objects.create(
            nombre="Redondo", sku="RB-002", marca=marca, categoria=categoria,
            material=material, color_marco="Negro", precio=Decimal("500.00"), stock=2,
        )
        self.tipo_lente = TipoLente.objects.create(nombre="Antirreflejo", precio_adicional=Decimal("200.00"))
        self.usuario = User.objects.create_user("pepe", password="1234")
        self.cliente = Cliente.objects.create(usuario=self.usuario, dni="30111222")
        self.client.login(username="pepe", password="1234")

    def crear_pedido(self, items, estado=Pedido.Estado.PENDIENTE):
        pedido = Pedido.objects.create(cliente=self.cliente, estado=estado)
        for anteojo, cantidad in items:
            DetallePedido.objects.create(pedido=pedido, anteojo=anteojo, cantidad=cantidad)
        return pedido


class PedidoCreateTests(VentasBaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/api/pedidos/"

    def test_create_pedido_calcula_total(self):
        data = {
            "cliente": self.cliente.id,
            "items": [
                {"anteojo_id": self.anteojo.id, "cantidad": 2, "tipo_lente_id": self.tipo_lente.id},
                {"anteojo_id": self.anteojo2.id, "cantidad": 1},
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # (1000 + 200) * 2 + 500 * 1 = 2900
        self.assertEqual(Decimal(response.data["total"]), Decimal("2900.00"))
        pedido = Pedido.objects.get(id=response.data["id"])
        self.assertEqual(pedido.detalles.count(), 2)
        self.assertEqual(pedido.estado, Pedido.Estado.PENDIENTE)

    def test_create_pedido_no_descuenta_stock(self):
        data = {"cliente": self.cliente.id, "items": [{"anteojo_id": self.anteojo.id, "cantidad": 2}]}
        self.client.post(self.url, data, format="json")
        self.anteojo.refresh_from_db()
        self.assertEqual(self.anteojo.stock, 5)

    def test_create_pedido_sin_auth(self):
        self.client.logout()
        data = {"cliente": self.cliente.id, "items": [{"anteojo_id": self.anteojo.id}]}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PedidoConfirmarTests(VentasBaseTestCase):
    def url(self, pedido):
        return f"/api/pedidos/{pedido.id}/confirmar/"

    def test_confirmar_pedido_descuenta_stock(self):
        pedido = self.crear_pedido([(self.anteojo, 2), (self.anteojo2, 1)])
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pedido.refresh_from_db()
        self.anteojo.refresh_from_db()
        self.anteojo2.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.PAGADO)
        self.assertEqual(self.anteojo.stock, 3)
        self.assertEqual(self.anteojo2.stock, 1)

    def test_confirmar_pedido_stock_insuficiente(self):
        # El primer item tiene stock, el segundo no: no debe descontarse nada
        pedido = self.crear_pedido([(self.anteojo, 1), (self.anteojo2, 3)])
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        pedido.refresh_from_db()
        self.anteojo.refresh_from_db()
        self.anteojo2.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.PENDIENTE)
        self.assertEqual(self.anteojo.stock, 5)
        self.assertEqual(self.anteojo2.stock, 2)

    def test_confirmar_pedido_ya_pagado(self):
        pedido = self.crear_pedido([(self.anteojo, 1)], estado=Pedido.Estado.PAGADO)
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.anteojo.refresh_from_db()
        self.assertEqual(self.anteojo.stock, 5)

    def test_confirmar_pedido_cancelado(self):
        pedido = self.crear_pedido([(self.anteojo, 1)], estado=Pedido.Estado.CANCELADO)
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirmar_pedido_vacio(self):
        pedido = self.crear_pedido([])
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirmar_pedido_ajeno(self):
        otro = User.objects.create_user("juana", password="1234")
        otro_cliente = Cliente.objects.create(usuario=otro, dni="30999888")
        pedido = Pedido.objects.create(cliente=otro_cliente)
        DetallePedido.objects.create(pedido=pedido, anteojo=self.anteojo, cantidad=1)
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PedidoCancelarTests(VentasBaseTestCase):
    def url(self, pedido):
        return f"/api/pedidos/{pedido.id}/cancelar/"

    def test_cancelar_pedido_pagado_restituye_stock(self):
        pedido = self.crear_pedido([(self.anteojo, 2)])
        self.client.post(f"/api/pedidos/{pedido.id}/confirmar/")
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pedido.refresh_from_db()
        self.anteojo.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.CANCELADO)
        self.assertEqual(self.anteojo.stock, 5)

    def test_cancelar_pedido_pendiente_no_modifica_stock(self):
        pedido = self.crear_pedido([(self.anteojo, 2)])
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.anteojo.refresh_from_db()
        self.assertEqual(self.anteojo.stock, 5)

    def test_cancelar_pedido_dos_veces(self):
        pedido = self.crear_pedido([(self.anteojo, 1)])
        self.client.post(self.url(pedido))
        response = self.client.post(self.url(pedido))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResenaTests(VentasBaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/api/resenas/"

    def test_create_resena(self):
        data = {"anteojo": self.anteojo.id, "puntaje": 4, "comentario": "Muy comodos"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resena.objects.get().cliente, self.cliente)

    def test_create_resena_duplicada(self):
        data = {"anteojo": self.anteojo.id, "puntaje": 4}
        self.client.post(self.url, data)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Resena.objects.count(), 1)

    def test_create_resena_puntaje_fuera_de_rango(self):
        for puntaje in (0, 6):
            response = self.client.post(self.url, {"anteojo": self.anteojo.id, "puntaje": puntaje})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Resena.objects.count(), 0)

    def test_create_resena_sin_auth(self):
        self.client.logout()
        response = self.client.post(self.url, {"anteojo": self.anteojo.id, "puntaje": 5})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
