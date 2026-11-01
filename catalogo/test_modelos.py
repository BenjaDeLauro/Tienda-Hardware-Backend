from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Marca, Presentacion, Producto, Proveedor, Resena


class CatalogoModelosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(username='cliente')
        cls.categoria = Categoria.objects.create(nombre='Cervezas')
        cls.marca = Marca.objects.create(nombre='Marca artesanal')
        cls.producto = Producto.objects.create(
            nombre='IPA', precio='2500.00', stock=10,
            categoria=cls.categoria, marca=cls.marca,
        )

    def test_hay_diez_modelos_propios_sin_contar_tablas_automaticas(self):
        modelos = [modelo for app in ('catalogo', 'usuarios', 'pedidos')
                   for modelo in apps.get_app_config(app).get_models()]
        self.assertEqual(len(modelos), 10)

    def test_producto_existente_no_necesita_presentacion_ni_proveedores(self):
        self.producto.full_clean()
        self.assertIsNone(self.producto.presentacion_id)
        self.assertEqual(self.producto.proveedores.count(), 0)

    def test_capacidad_cero_se_rechaza_en_validacion_y_base_de_datos(self):
        presentacion = Presentacion(nombre='Lata', capacidad_ml=0)
        with self.assertRaises(ValidationError):
            presentacion.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            presentacion.save()

    def test_presentacion_admite_varias_capacidades_pero_no_duplicados(self):
        Presentacion.objects.create(nombre='Lata', capacidad_ml=473)
        Presentacion.objects.create(nombre='Lata', capacidad_ml=330)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Presentacion.objects.create(nombre='Lata', capacidad_ml=473)

    def test_presentacion_usada_no_se_elimina(self):
        presentacion = Presentacion.objects.create(nombre='Lata', capacidad_ml=473)
        self.producto.presentacion = presentacion
        self.producto.save()
        with self.assertRaises(ProtectedError):
            presentacion.delete()

    def test_producto_admite_varios_proveedores_y_proveedor_varios_productos(self):
        proveedor = Proveedor.objects.create(nombre='Distribuidora local')
        otro_proveedor = Proveedor.objects.create(nombre='Distribuidora regional')
        otro_producto = Producto.objects.create(
            nombre='Porter', precio='2700.00', stock=5,
            categoria=self.categoria, marca=self.marca,
        )
        self.producto.proveedores.add(proveedor, otro_proveedor)
        otro_producto.proveedores.add(proveedor)
        self.assertEqual(self.producto.proveedores.count(), 2)
        self.assertEqual(proveedor.productos.count(), 2)
        proveedor.delete()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.proveedores.count(), 1)

    def test_calificacion_fuera_de_rango_se_rechaza_incluso_sin_full_clean(self):
        for calificacion in (0, 6):
            with self.subTest(calificacion=calificacion):
                resena = Resena(usuario=self.usuario, producto=self.producto,
                                calificacion=calificacion)
                with self.assertRaises(ValidationError):
                    resena.full_clean()
                with self.assertRaises(IntegrityError), transaction.atomic():
                    resena.save()

    def test_una_resena_por_usuario_y_producto_permite_editar(self):
        resena = Resena.objects.create(
            usuario=self.usuario, producto=self.producto, calificacion=5,
        )
        resena.calificacion = 4
        resena.full_clean()
        resena.save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Resena.objects.create(
                usuario=self.usuario, producto=self.producto, calificacion=3,
            )
        self.assertEqual(self.producto.resenas.get().calificacion, 4)

    def test_eliminar_producto_elimina_sus_resenas(self):
        Resena.objects.create(usuario=self.usuario, producto=self.producto, calificacion=1)
        self.producto.delete()
        self.assertFalse(Resena.objects.exists())


class AdministracionModelosTests(TestCase):
    def test_administrador_accede_a_listados_y_formularios_de_modelos_nuevos(self):
        admin = get_user_model().objects.create_user(
            username='administrador', is_staff=True, is_superuser=True,
        )
        self.client.force_login(admin)
        for modelo in ('catalogo_presentacion', 'catalogo_proveedor',
                       'catalogo_resena', 'usuarios_direccionenvio'):
            for vista in ('changelist', 'add'):
                with self.subTest(modelo=modelo, vista=vista):
                    respuesta = self.client.get(reverse(f'admin:{modelo}_{vista}'))
                    self.assertEqual(respuesta.status_code, 200)
