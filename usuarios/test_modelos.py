from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from pedidos.models import Pedido
from .models import DireccionEnvio


class DireccionEnvioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(username='cliente')
        cls.direccion = DireccionEnvio.objects.create(
            usuario=cls.usuario, destinatario='Cliente de prueba',
            calle='San Martin', numero='100', ciudad='Rio Cuarto',
            provincia='Cordoba', codigo_postal='5800',
        )

    def test_usuario_puede_registrar_varias_direcciones(self):
        DireccionEnvio.objects.create(
            usuario=self.usuario, destinatario='Cliente de prueba',
            calle='Belgrano', numero='200', ciudad='Rio Cuarto',
            provincia='Cordoba', codigo_postal='5800',
        )
        self.assertEqual(self.usuario.direcciones_envio.count(), 2)

    def test_direccion_usada_en_pedido_no_se_elimina(self):
        Pedido.objects.create(usuario=self.usuario, direccion_envio=self.direccion)
        with self.assertRaises(ProtectedError):
            self.direccion.delete()

    def test_eliminar_usuario_sin_pedidos_elimina_sus_direcciones(self):
        self.usuario.delete()
        self.assertFalse(DireccionEnvio.objects.exists())
