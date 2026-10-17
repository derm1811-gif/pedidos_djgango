from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Pedido


class RegistroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].help_text = (
            'Obligatorio. Hasta 150 caracteres; usa letras, números y @/./+/-/_. '
        )
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'username',
            'autofocus': True,
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = (
            'Usa al menos 8 caracteres. Evita contraseñas comunes, solo numéricas '
            'o demasiado similares a tus datos personales.'
        )
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password2'].help_text = 'Escribe la misma contraseña otra vez para confirmarla.'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'numero_pedido',
            'cliente',
            'descripcion',
            'valor_total',
            'estado',
        ]
        labels = {
            'numero_pedido': 'Número de pedido',
            'cliente': 'Nombre del cliente',
            'descripcion': 'Descripción del pedido',
            'valor_total': 'Valor total',
            'estado': 'Estado del pedido',
        }
        error_messages = {
            'numero_pedido': {
                'required': 'El número del pedido es obligatorio.',
                'unique': 'Ya existe un pedido con ese número.',
            },
            'cliente': {'required': 'El nombre del cliente es obligatorio.'},
            'descripcion': {'required': 'La descripción del pedido es obligatoria.'},
            'valor_total': {
                'required': 'El valor total es obligatorio.',
                'invalid': 'Escribe un valor numérico válido.',
                'min_value': 'El valor total debe ser mayor que cero.',
            },
            'estado': {'invalid_choice': 'Selecciona un estado permitido.'},
        }
        widgets = {
            'numero_pedido': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'maxlength': 30,
            }),
            'cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'minlength': 3,
                'maxlength': 120,
                'autocomplete': 'name',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 1500,
            }),
            'valor_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_numero_pedido(self):
        return self.cleaned_data['numero_pedido'].strip()

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente'].strip()
        if len(cliente) < 3:
            raise forms.ValidationError('El nombre del cliente debe tener al menos 3 caracteres.')
        return cliente

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion'].strip()
        if not descripcion:
            raise forms.ValidationError('La descripción del pedido es obligatoria.')
        return descripcion


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'username',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
        }),
    )