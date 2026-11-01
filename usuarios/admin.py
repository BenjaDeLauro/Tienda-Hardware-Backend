from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import DireccionEnvio, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active'
    )

    list_filter = ('is_staff', 'is_active', 'groups')

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )

    ordering = ('username',)


@admin.register(DireccionEnvio)
class DireccionEnvioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'destinatario', 'calle', 'numero', 'ciudad', 'provincia')
    list_filter = ('pais', 'provincia', 'ciudad')
    search_fields = ('usuario__username', 'destinatario', 'calle', 'codigo_postal')
    ordering = ('ciudad', 'calle', 'numero')
    list_select_related = ('usuario',)
    autocomplete_fields = ('usuario',)
