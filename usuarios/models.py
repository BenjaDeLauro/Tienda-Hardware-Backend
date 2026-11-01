from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class Usuario(AbstractUser):
    def __str__(self):
        return self.username


class DireccionEnvio(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='direcciones_envio',
    )
    destinatario = models.CharField(max_length=150)
    calle = models.CharField(max_length=150)
    numero = models.CharField(max_length=20)
    piso_departamento = models.CharField(max_length=40, blank=True)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    pais = models.CharField(max_length=100, default='Argentina')
    telefono = models.CharField(max_length=25, blank=True)

    class Meta:
        verbose_name = 'dirección de envío'
        verbose_name_plural = 'direcciones de envío'
        ordering = ('ciudad', 'calle', 'numero')

    def __str__(self):
        return f'{self.destinatario}: {self.calle} {self.numero}, {self.ciudad}'

    def clean(self):
        super().clean()
        if self.pk and self.usuario_id:
            if self.pedidos.exclude(usuario_id=self.usuario_id).exists():
                raise ValidationError({
                    'usuario': 'Una dirección usada en pedidos no puede pasar a otro usuario.',
                })
