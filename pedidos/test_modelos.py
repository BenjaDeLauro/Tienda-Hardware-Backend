from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase

from usuarios.models import DireccionEnvio
from .models import Pedido


class PedidoDireccionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(username='cliente')
        cls.otro_usuario = get_user_model().objects.create_user(username='otro_cliente')
        cls.direccion = DireccionEnvio.objects.create(
            usuario=cls.usuario, destinatario='Cliente de prueba',
            calle='San Martin', numero='100', ciudad='Rio Cuarto',
            provincia='Cordoba', codigo_postal='5800',
        )

    def test_pedido_existente_sin_direccion_sigue_siendo_valido(self):
        pedido = Pedido.objects.create(usuario=self.usuario)
        pedido.full_clean()
        self.assertIsNone(pedido.direccion_envio_id)

    def test_pedido_acepta_direccion_de_su_usuario(self):
        pedido = Pedido(usuario=self.usuario, direccion_envio=self.direccion)
        pedido.full_clean()
        pedido.save()
        self.assertEqual(self.direccion.pedidos.get(), pedido)

    def test_modelo_y_formulario_rechazan_direccion_de_otro_usuario(self):
        pedido = Pedido(usuario=self.otro_usuario, direccion_envio=self.direccion)
        with self.assertRaises(ValidationError) as error:
            pedido.full_clean()
        self.assertIn('direccion_envio', error.exception.message_dict)
        formulario = modelform_factory(
            Pedido, fields=('usuario', 'direccion_envio', 'estado'),
        )(data={
            'usuario': self.otro_usuario.pk,
            'direccion_envio': self.direccion.pk,
            'estado': 'pendiente',
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn('direccion_envio', formulario.errors)

    def test_direccion_inexistente_devuelve_error_de_validacion(self):
        pedido = Pedido(usuario=self.usuario, direccion_envio_id=99999)
        with self.assertRaises(ValidationError) as error:
            pedido.full_clean()
        self.assertIn('direccion_envio', error.exception.message_dict)

    def test_direccion_usada_no_puede_reasignarse_a_otro_usuario(self):
        Pedido.objects.create(usuario=self.usuario, direccion_envio=self.direccion)
        self.direccion.usuario = self.otro_usuario
        with self.assertRaises(ValidationError) as error:
            self.direccion.full_clean()
        self.assertIn('usuario', error.exception.message_dict)
