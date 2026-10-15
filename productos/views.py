from django.shortcuts import render
from .models import Producto
# Create your views here.

#crear producto 
def crear_producto(request):
    if request.method == 'POST':
        
        prodoductos = Producto(
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            precio=request.POST['precio'],
            cantidad_disponible=request.POST['cantidad_disponible'],
            fecha_registro=request.POST['fecha_registro']
        )
        
        prodoductos.save()
        return render(request, 'productos/formulario.html', {'mensaje': 'Producto creado correctamente'})
    