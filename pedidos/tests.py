from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Pedido


class PedidoViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='aprendiz',
            password='ClaveSegura123!',
        )

    def order_data(self, **overrides):
        data = {
            'numero_pedido': 'PED-1001',
            'cliente': 'Cliente de prueba',
            'descripcion': 'Pedido de prueba',
            'valor_total': '125000.00',
            'estado': Pedido.Estado.PENDIENTE,
        }
        data.update(overrides)
        return data

    def test_private_order_pages_redirect_to_login(self):
        response = self.client.get(reverse('pedidos:lista'))
        self.assertRedirects(
            response,
            f'{reverse("pedidos:login")}?next={reverse("pedidos:lista")}',
        )

    def test_invalid_credentials_show_message(self):
        response = self.client.post(reverse('pedidos:login'), {
            'username': self.user.username,
            'password': 'incorrecta',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos.')

    def test_login_and_logout(self):
        response = self.client.post(reverse('pedidos:login'), {
            'username': self.user.username,
            'password': 'ClaveSegura123!',
        })
        self.assertRedirects(response, reverse('pedidos:lista'))
        response = self.client.post(reverse('pedidos:logout'))
        self.assertRedirects(response, reverse('pedidos:login'))
        response = self.client.get(reverse('pedidos:lista'))
        self.assertRedirects(
            response,
            f'{reverse("pedidos:login")}?next={reverse("pedidos:lista")}',
        )

    def test_registration_creates_hashed_password_and_redirects_to_login(self):
        response = self.client.post(reverse('pedidos:registro'), {
            'username': 'nuevo_aprendiz',
            'password1': 'MiClaveSegura2026!',
            'password2': 'MiClaveSegura2026!',
        }, follow=True)
        self.assertRedirects(response, reverse('pedidos:login'))
        self.assertContains(response, 'Cuenta creada correctamente. Inicia sesión para continuar.')
        new_user = get_user_model().objects.get(username='nuevo_aprendiz')
        self.assertTrue(new_user.check_password('MiClaveSegura2026!'))
        self.assertNotEqual(new_user.password, 'MiClaveSegura2026!')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('pedidos:registro'), {
            'username': 'nuevo_aprendiz',
            'password1': 'MiClaveSegura2026!',
            'password2': 'OtraClaveSegura2026!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username='nuevo_aprendiz').exists())

    def test_registration_help_is_in_spanish(self):
        response = self.client.get(reverse('pedidos:registro'))
        self.assertContains(response, 'Usa al menos 8 caracteres.')
        self.assertNotContains(response, 'Your password must contain')

    def test_order_form_labels_are_in_spanish(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('pedidos:crear'))
        self.assertContains(response, 'Número de pedido')
        self.assertContains(response, 'Descripción del pedido')

    def test_create_associates_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('pedidos:crear'), self.order_data())
        pedido = Pedido.objects.get(numero_pedido='PED-1001')
        self.assertRedirects(response, reverse('pedidos:detalle', args=[pedido.pk]))
        self.assertEqual(pedido.usuario, self.user)

    def test_duplicate_order_number_is_rejected(self):
        Pedido.objects.create(
            **self.order_data(),
            usuario=self.user,
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse('pedidos:crear'), self.order_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors['numero_pedido'],
            ['Ya existe un pedido con ese número.'],
        )
        self.assertEqual(Pedido.objects.filter(numero_pedido='PED-1001').count(), 1)

    def test_edit_can_change_order_status(self):
        pedido = Pedido.objects.create(
            **self.order_data(),
            usuario=self.user,
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('pedidos:editar', args=[pedido.pk]),
            self.order_data(estado=Pedido.Estado.CONFIRMADO),
        )
        pedido.refresh_from_db()
        self.assertRedirects(response, reverse('pedidos:detalle', args=[pedido.pk]))
        self.assertEqual(pedido.estado, Pedido.Estado.CONFIRMADO)
        self.assertEqual(pedido.usuario, self.user)

    def test_delete_requires_confirmation_and_post(self):
        pedido = Pedido.objects.create(
            **self.order_data(),
            usuario=self.user,
        )
        self.client.force_login(self.user)
        confirmation = self.client.get(reverse('pedidos:eliminar', args=[pedido.pk]))
        self.assertEqual(confirmation.status_code, 200)
        self.assertTrue(Pedido.objects.filter(pk=pedido.pk).exists())
        response = self.client.post(reverse('pedidos:eliminar', args=[pedido.pk]))
        self.assertRedirects(response, reverse('pedidos:lista'))
        self.assertFalse(Pedido.objects.filter(pk=pedido.pk).exists())

    def test_non_positive_total_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('pedidos:crear'),
            self.order_data(valor_total='0'),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('valor_total', response.context['form'].errors)
        self.assertFalse(Pedido.objects.exists())