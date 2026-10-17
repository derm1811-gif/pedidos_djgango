from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Producto
# Create your views here.


def leer_datos_producto(request):
    nombre = request.POST.get('nombre', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    precio_ingresado = request.POST.get('precio', '').strip()
    cantidad_ingresada = request.POST.get('cantidad_disponible', '').strip()
    estado = request.POST.get('estado') == 'true'
    errores = {}

    if not nombre:
        errores['nombre'] = 'El nombre es obligatorio.'
    elif len(nombre) < 3:
        errores['nombre'] = 'El nombre debe tener al menos 3 caracteres.'

    longitud_descripcion = Producto._meta.get_field('descripcion').max_length
    if not descripcion:
        errores['descripcion'] = 'La descripción es obligatoria.'
    elif len(descripcion) > longitud_descripcion:
        errores['descripcion'] = f'La descripción no puede superar {longitud_descripcion} caracteres.'

    try:
        precio = Decimal(precio_ingresado)
        if not precio.is_finite() or precio <= 0:
            errores['precio'] = 'El precio debe ser un número mayor que cero.'
        elif precio.as_tuple().exponent < -2:
            errores['precio'] = 'El precio admite máximo dos decimales.'
        elif precio >= Decimal('100000000'):
            errores['precio'] = 'El precio no puede superar 99.999.999,99.'
    except InvalidOperation:
        precio = None
        errores['precio'] = 'Escribe un precio válido.'

    try:
        cantidad = int(cantidad_ingresada)
        if cantidad < 0:
            errores['cantidad_disponible'] = 'La cantidad no puede ser negativa.'
    except ValueError:
        cantidad = None
        errores['cantidad_disponible'] = 'La cantidad debe ser un número entero.'

    datos = {
        'nombre': nombre,
        'descripcion': descripcion,
        'precio': precio_ingresado,
        'cantidad_disponible': cantidad_ingresada,
        'estado': estado,
    }
    valores_validos = {
        'nombre': nombre,
        'descripcion': descripcion,
        'precio': precio,
        'cantidad_disponible': cantidad,
        'estado': estado,
    }
    return datos, valores_validos, errores


@login_required
def crear_producto(request):
    if request.method == 'POST':
        datos, valores, errores = leer_datos_producto(request)
        if errores:
            return render(request, 'productos/formulario.html', {
                'producto': None,
                'datos': datos,
                'errores': errores,
                'estado_marcado': datos['estado'],
                'titulo': 'Nuevo producto',
            })

        productos = Producto(**valores)
        productos.save()
        return render(request, 'productos/formulario.html', {
            'producto': None,
            'mensaje': 'Producto creado correctamente',
            'estado_marcado': True,
            'titulo': 'Nuevo producto',
        })

    return render(request, 'productos/formulario.html', {
        'producto': None,
        'estado_marcado': True,
        'titulo': 'Nuevo producto',
    })

# LISTAR
@login_required
def listar(request):
    consulta = request.GET.get('q', '').strip()
    productos = Producto.objects.all()
    if consulta:
        productos = productos.filter(nombre__icontains=consulta)

    return render(
        request,
        "productos/lista.html",
        {"productos": productos, "consulta": consulta}
    )


# VER
@login_required
def detalle(request, id):

    producto = get_object_or_404(Producto, id=id)

    return render(
        request,
        "productos/detalle.html",
        {"producto": producto}
    )


# EDITAR
@login_required
def editar(request, id):

    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        datos, valores, errores = leer_datos_producto(request)
        if errores:
            return render(request, 'productos/formulario.html', {
                'producto': producto,
                'datos': datos,
                'errores': errores,
                'estado_marcado': datos['estado'],
                'titulo': f'Editar {producto.nombre}',
            })

        producto.nombre = valores['nombre']
        producto.descripcion = valores['descripcion']
        producto.precio = valores['precio']
        producto.cantidad_disponible = valores['cantidad_disponible']
        producto.estado = valores['estado']

        producto.save()

        return render(
            request,
            "productos/formulario.html",
            {
                "producto": producto,
                "mensaje": "Producto actualizado correctamente",
                "estado_marcado": producto.estado,
                "titulo": f'Editar {producto.nombre}',
            }
        )

    return render(
        request,
        "productos/formulario.html",
        {"producto": producto, "estado_marcado": producto.estado, "titulo": f'Editar {producto.nombre}'}
    )


# ELIMINAR
@login_required
def eliminar(request, id):

    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        return render(request, 'productos/lista.html', {
            'productos': Producto.objects.all(),
            'mensaje': f'Producto "{nombre}" eliminado correctamente.',
        })

    return render(
        request,
        'productos/confirmar_eliminacion.html',
        {'producto': producto},
    )