from django import forms
from .models import Comentario


class FormularioComentario(forms.ModelForm):
    """Formulario para enviar comentarios en la página de detalle de un juego."""
    # El campo texto se muestra con un textarea para entradas de usuario en la vista.

    class Meta:
        model = Comentario
        fields = ['texto']
        labels = {'texto': ''}
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 3, 'class': 'form-control',
                'placeholder': 'Escribe tu comentario...','maxlength': '1000',
            }),
        }

