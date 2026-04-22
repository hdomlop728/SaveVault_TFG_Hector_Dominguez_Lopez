from django import forms

from .models import ReporteComentario, ReporteGuardado


class FormularioReporteGuardado(forms.ModelForm):
    # Formulario para enviar un reporte sobre un archivo de guardado.
    class Meta:
        model = ReporteGuardado
        fields = ['motivo', 'detalle']
        labels = {'motivo': 'Motivo', 'detalle': 'Detalle adicional'}
        widgets = {
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'detalle': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Añade información adicional...',
                    'maxlength': '500',
                }
            ),
        }
        error_messages = {'motivo': {'required': 'Selecciona un motivo.'}}


class FormularioReporteComentario(forms.ModelForm):
    # Formulario para enviar un reporte sobre un comentario de usuario.
    class Meta:
        model = ReporteComentario
        fields = ['motivo', 'detalle']
        labels = {'motivo': 'Motivo', 'detalle': 'Detalle adicional'}
        widgets = {
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'detalle': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Añade información adicional...',
                    'maxlength': '500',
                }
            ),
        }
        error_messages = {'motivo': {'required': 'Selecciona un motivo.'}}
