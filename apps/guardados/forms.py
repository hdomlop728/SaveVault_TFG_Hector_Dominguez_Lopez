from django import forms
from .models import ArchivoGuardado
from .validators import validar_extension_guardado, validar_tamanio_guardado
from apps.juegos.models import Juego


class FormularioGuardado(forms.ModelForm):
    class Meta:
        model = ArchivoGuardado
        fields = ['juego', 'region', 'archivo', 'descripcion']
        labels = {'juego':'Juego','region':'Región','archivo':'Archivo de guardado','descripcion':'Descripción'}
        widgets = {
            'juego':      forms.Select(attrs={'class':'form-select','id':'id_juego'}),
            'region':     forms.Select(attrs={'class':'form-select'}),
            'archivo':    forms.FileInput(attrs={'class':'form-control'}),
            'descripcion':forms.TextInput(attrs={'class':'form-control','placeholder':'Descripción opcional (ej. Jefe final, 100% completado...)'}),
        }
        error_messages = {
            'juego':   {'required':'Selecciona un juego.'},
            'region':  {'required':'Selecciona una región.'},
            'archivo': {'required':'El archivo de guardado es obligatorio.'},
        }

    def __init__(self, *args, juego=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixed_game = juego
        if juego:
            # Si el formulario se crea con un juego predeterminado, forzamos ese juego.
            self.fields['juego'].initial = juego
            self.fields['juego'].queryset = Juego.objects.filter(pk=juego.pk)
            self.fields['juego'].widget = forms.HiddenInput()
        else:
            # Si no hay juego preseleccionado, el usuario puede elegir uno de todos los juegos.
            qs = Juego.objects.select_related('plataforma').order_by('plataforma__nombre', 'titulo')
            self.fields['juego'].queryset = qs
            self.fields['juego'].label_from_instance = lambda obj: f"{obj.titulo} ({obj.plataforma.nombre})"
            self.fields['juego'].empty_label = 'Selecciona un juego'

    def clean(self):
        datos = super().clean()
        archivo = datos.get('archivo')
        juego   = datos.get('juego')
        if archivo and juego:
            # Validar la extensión y el tamaño del archivo después de haber enlazado el juego.
            try:
                validar_extension_guardado(archivo, juego.plataforma_id, juego.plataforma.nombre)
                validar_tamanio_guardado(archivo)
            except forms.ValidationError as e:
                self.add_error('archivo', e)
        return datos

