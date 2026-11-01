from django.contrib import admin
from .models import Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'fecha',
        'estado',
        'direccion_envio',
    )

    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__username',)
    ordering = ('-fecha',)
    list_select_related = ('usuario', 'direccion_envio')
    autocomplete_fields = ('usuario', 'direccion_envio')

    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'pedido',
        'producto',
        'cantidad',
        'precio_unitario',
        'subtotal'
    )

    search_fields = ('producto__nombre',)
    ordering = ('id',)
