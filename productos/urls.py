from django.urls import path
from . import views

urlpatterns = [
    path("", views.crear_producto),
    path("lista/", views.listar),
    path("detalle/<int:id>/", views.detalle),
    path("editar/<int:id>/", views.editar),
    path("eliminar/<int:id>/", views.eliminar),
]