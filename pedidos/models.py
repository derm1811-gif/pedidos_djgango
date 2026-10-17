from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        CANCELADO = 'cancelado', 'Cancelado'

    numero_pedido = models.CharField(max_length=30, unique=True)
    cliente = models.CharField(max_length=120)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(max_length=1500)
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos_registrados',
    )

    class Meta:
        ordering = ['-fecha_registro', '-id']
        constraints = [
            models.CheckConstraint(
                condition=Q(valor_total__gt=0),
                name='pedido_valor_total_positivo',
            ),
            models.CheckConstraint(
                condition=Q(estado__in=['pendiente', 'confirmado', 'cancelado']),
                name='pedido_estado_permitido',
            ),
        ]

    def __str__(self):
        return self.numero_pedido