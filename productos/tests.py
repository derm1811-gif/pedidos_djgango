from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Producto


class ProductoViewsTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='inventario',
			password='ClaveSegura123!',
		)

	def datos_producto(self, **overrides):
		datos = {
			'nombre': 'Teclado',
			'descripcion': 'Teclado mecanico',
			'precio': '120000.00',
			'cantidad_disponible': '4',
			'estado': 'true',
		}
		datos.update(overrides)
		return datos

	def test_product_pages_require_login(self):
		response = self.client.get('/productos/lista/')
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.url.startswith('/pedidos/login/'))

	def test_invalid_product_values_are_not_saved(self):
		self.client.force_login(self.user)
		response = self.client.post(
			'/productos/',
			self.datos_producto(
				nombre='AB',
				descripcion='x' * 1001,
				precio='-1',
				cantidad_disponible='2.5',
			),
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			set(response.context['errores']),
			{'nombre', 'descripcion', 'precio', 'cantidad_disponible'},
		)
		self.assertFalse(Producto.objects.exists())

	def test_valid_product_is_saved(self):
		self.client.force_login(self.user)
		response = self.client.post('/productos/', self.datos_producto())
		self.assertEqual(response.status_code, 200)
		producto = Producto.objects.get(nombre='Teclado')
		self.assertEqual(producto.cantidad_disponible, 4)
		self.assertTrue(producto.estado)

	def test_edit_can_mark_product_unavailable(self):
		producto = Producto.objects.create(
			nombre='Teclado',
			descripcion='Teclado mecanico',
			precio='120000.00',
			cantidad_disponible=4,
			estado=True,
		)
		self.client.force_login(self.user)
		datos = self.datos_producto(estado='false')
		datos.pop('estado')
		response = self.client.post(f'/productos/editar/{producto.pk}/', datos)
		self.assertEqual(response.status_code, 200)
		producto.refresh_from_db()
		self.assertFalse(producto.estado)

	def test_price_outside_model_precision_is_rejected(self):
		self.client.force_login(self.user)
		response = self.client.post(
			'/productos/',
			self.datos_producto(precio='100000000'),
		)
		self.assertEqual(response.status_code, 200)
		self.assertIn('precio', response.context['errores'])
		self.assertFalse(Producto.objects.exists())

	def test_product_deletion_requires_confirmation_and_post(self):
		producto = Producto.objects.create(
			nombre='Teclado',
			descripcion='Teclado mecanico',
			precio='120000.00',
			cantidad_disponible=4,
		)
		self.client.force_login(self.user)
		confirmation = self.client.get(f'/productos/eliminar/{producto.pk}/')
		self.assertEqual(confirmation.status_code, 200)
		self.assertTrue(Producto.objects.filter(pk=producto.pk).exists())
		response = self.client.post(f'/productos/eliminar/{producto.pk}/')
		self.assertEqual(response.status_code, 200)
		self.assertFalse(Producto.objects.filter(pk=producto.pk).exists())
