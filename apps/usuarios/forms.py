from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, validar_avatar
import base64, io
from django.core.files.base import ContentFile
from PIL import Image as PILImage


def procesar_avatar(avatar_original, avatar_crop_data):
    """Convierte el avatar a PNG — desde crop o desde archivo directo."""
    from django.core.exceptions import ValidationError as DjangoValidationError

    # Si hay crop, usar ese — ya tiene 800x800 garantizado
    if avatar_crop_data and avatar_crop_data.startswith('data:image'):
        try:
            _, imgstr = avatar_crop_data.split(';base64,')
            return ContentFile(base64.b64decode(imgstr), name='avatar.png')
        except Exception as e:
            raise forms.ValidationError(f'Error procesando la imagen recortada: {e}')

    # Sin crop — validar y convertir a PNG manteniendo resolución original
    if avatar_original and hasattr(avatar_original, 'size'):
        validar_avatar(avatar_original)  # lanza ValidationError si falla
        avatar_original.seek(0)
        img = PILImage.open(avatar_original)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        return ContentFile(buffer.read(), name='avatar.png')

    return avatar_original


class FormularioRegistro(UserCreationForm):
    email       = forms.EmailField(required=True, label='Correo electrónico', widget=forms.EmailInput(attrs={'class':'form-control'}))
    bio         = forms.CharField(required=False, label='Biografía', max_length=500, widget=forms.Textarea(attrs={'class':'form-control','rows':3}))
    avatar      = forms.ImageField(required=False, label='Avatar', widget=forms.FileInput(attrs={'class':'form-control','accept':'image/*','id':'id_avatar_registro'}))
    avatar_crop = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Usuario
        fields = ['username','email','password1','password2','bio','avatar']
        labels = {'username':'Nombre de usuario'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        for f in self.fields.values():
            if 'class' not in f.widget.attrs: f.widget.attrs['class'] = 'form-control'

    def clean(self):
        datos = super().clean()
        try:
            datos['avatar'] = procesar_avatar(
                datos.get('avatar'),
                self.data.get('avatar_crop', '')
            )
        except forms.ValidationError as e:
            self.add_error('avatar', e)
        return datos


class FormularioEditarPerfil(forms.ModelForm):
    avatar      = forms.ImageField(required=False, label='Avatar', widget=forms.FileInput(attrs={'class':'form-control','accept':'image/*','id':'id_avatar_editar'}))
    avatar_crop = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Usuario
        fields = ['username','email','first_name','last_name','bio','avatar']
        labels = {'username':'Nombre de usuario','email':'Correo electrónico','first_name':'Nombre','last_name':'Apellidos','bio':'Biografía'}
        widgets = {
            'username':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.EmailInput(attrs={'class':'form-control'}),
            'first_name':forms.TextInput(attrs={'class':'form-control'}),
            'last_name':forms.TextInput(attrs={'class':'form-control'}),
            'bio':forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and Usuario.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean(self):
        datos = super().clean()
        try:
            datos['avatar'] = procesar_avatar(
                datos.get('avatar'),
                self.data.get('avatar_crop', '')
            )
        except forms.ValidationError as e:
            self.add_error('avatar', e)
        return datos


class FormularioLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password'].label = 'Contraseña'
        for f in self.fields.values(): f.widget.attrs['class'] = 'form-control'
