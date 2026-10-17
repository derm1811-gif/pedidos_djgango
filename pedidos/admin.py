from django.contrib import admin

from .models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'cliente', 'valor_total', 'estado', 'usuario', 'fecha_registro')
    list_filter = ('estado',)
    search_fields = ('numero_pedido', 'cliente')