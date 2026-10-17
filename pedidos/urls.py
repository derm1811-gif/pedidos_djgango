from django.urls import path

from . import views

app_name = 'pedidos'

urlpatterns = [
    path('login/', views.iniciar_sesion, name='login'),
    path('registro/', views.registrar, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('', views.listar, name='lista'),
    path('nuevo/', views.crear, name='crear'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
]