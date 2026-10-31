from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Presentacion(models.Model):
    nombre = models.CharField(max_length=80)
    capacidad_ml = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'presentación'
        verbose_name_plural = 'presentaciones'
        ordering = ('nombre', 'capacidad_ml')
        constraints = [
            models.UniqueConstraint(
                fields=('nombre', 'capacidad_ml'),
                name='presentacion_nombre_capacidad_unica',
            ),
            models.CheckConstraint(
                condition=models.Q(capacidad_ml__gt=0),
                name='presentacion_capacidad_positiva',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} de {self.capacidad_ml} ml'


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=25, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'proveedores'
        ordering = ('nombre',)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos'
    )

    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name='productos'
    )

    presentacion = models.ForeignKey(
        Presentacion,
        on_delete=models.PROTECT,
        related_name='productos',
        blank=True,
        null=True,
    )
    proveedores = models.ManyToManyField(
        Proveedor,
        related_name='productos',
        blank=True,
    )

    def __str__(self):
        return self.nombre


class Resena(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resenas',
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='resenas',
    )
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'reseña'
        verbose_name_plural = 'reseñas'
        ordering = ('-fecha', '-pk')
        constraints = [
            models.UniqueConstraint(
                fields=('usuario', 'producto'),
                name='resena_usuario_producto_unica',
            ),
            models.CheckConstraint(
                condition=models.Q(calificacion__gte=1, calificacion__lte=5),
                name='resena_calificacion_entre_1_y_5',
            ),
        ]

    def __str__(self):
        return f'{self.producto} - {self.calificacion}/5 ({self.usuario})'
