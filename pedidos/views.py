from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, PedidoForm, RegistroForm
from .models import Pedido


def iniciar_sesion(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if usuario is not None:
            login(request, usuario)
            return redirect('pedidos:lista')
        form.add_error(None, 'Usuario o contraseña incorrectos.')
    return render(request, 'pedidos/login.html', {'form': form})


def registrar(request):
    if request.user.is_authenticated:
        return redirect('pedidos:lista')

    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cuenta creada correctamente. Inicia sesión para continuar.')
        return redirect('pedidos:login')
    return render(request, 'pedidos/registro.html', {'form': form})


def cerrar_sesion(request):
    if request.method == 'POST':
        logout(request)
    return redirect('pedidos:login')


@login_required
def listar(request):
    consulta = request.GET.get('q', '').strip()
    pedidos = Pedido.objects.select_related('usuario')
    if consulta:
        pedidos = pedidos.filter(
            Q(cliente__icontains=consulta)
            | Q(numero_pedido__icontains=consulta)
        )
    return render(request, 'pedidos/lista.html', {
        'pedidos': pedidos,
        'consulta': consulta,
    })


@login_required
def crear(request):
    form = PedidoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        pedido = form.save(commit=False)
        pedido.usuario = request.user
        pedido.save()
        messages.success(request, f'Pedido {pedido.numero_pedido} registrado correctamente.')
        return redirect('pedidos:detalle', pk=pedido.pk)
    return render(request, 'pedidos/formulario.html', {
        'form': form,
        'titulo': 'Registrar pedido',
        'accion': 'Registrar pedido',
    })


@login_required
def detalle(request, pk):
    pedido = get_object_or_404(Pedido.objects.select_related('usuario'), pk=pk)
    return render(request, 'pedidos/detalle.html', {'pedido': pedido})


@login_required
def editar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoForm(request.POST or None, instance=pedido)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Pedido {pedido.numero_pedido} actualizado correctamente.')
        return redirect('pedidos:detalle', pk=pedido.pk)
    return render(request, 'pedidos/formulario.html', {
        'form': form,
        'pedido': pedido,
        'titulo': f'Editar pedido {pedido.numero_pedido}',
        'accion': 'Guardar cambios',
    })


@login_required
def eliminar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        numero = pedido.numero_pedido
        pedido.delete()
        messages.success(request, f'Pedido {numero} eliminado.')
        return redirect('pedidos:lista')
    return render(request, 'pedidos/confirmar_eliminacion.html', {'pedido': pedido})