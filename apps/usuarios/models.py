import datetime
import os, shutil
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

def ruta_avatar(instance, filename):
    """Devuelve la ruta de almacenamiento del avatar de usuario en media/perfiles."""
    # Siempre guardar como .png (el cropper exporta en PNG)
    return f'perfiles/{instance.username}/avatar.png'



def validar_avatar(imagen):
    """Valida tamaño y resolución del avatar. Compartida entre modelo y formularios."""
    from PIL import Image as PILImage
    max_size = getattr(settings, 'PROFILE_IMAGE_MAX_SIZE', 5 * 1024 * 1024)
    if hasattr(imagen, 'size') and imagen.size > max_size:
        raise ValidationError(f'Imagen demasiado grande. Máximo: {max_size // (1024*1024)} MB.')
    try:
        if hasattr(imagen, 'seek'): imagen.seek(0)
        img = PILImage.open(imagen)
        max_w, max_h = getattr(settings, 'PROFILE_IMAGE_MAX_RESOLUTION', (800, 800))
        if img.width > max_w or img.height > max_h:
            raise ValidationError(f'Resolución demasiado alta. Máximo: {max_w}×{max_h}px.')
        if hasattr(imagen, 'seek'): imagen.seek(0)
    except ValidationError:
        raise
    except Exception:
        raise ValidationError('No se pudo leer el archivo de imagen.')



class Usuario(AbstractUser):
    """Usuario extendido con avatar, biografía y sistema de reportes/baneo."""
    email  = models.EmailField(unique=True, verbose_name='Correo electrónico')
    bio    = models.TextField(blank=True, max_length=500, verbose_name='Biografía')
    avatar = models.ImageField(upload_to=ruta_avatar, null=True, blank=True, verbose_name='Avatar')
    reportes_confirmados = models.PositiveSmallIntegerField(default=0, verbose_name='Reportes confirmados')
    baneo_hasta = models.DateTimeField(null=True, blank=True, verbose_name='Baneado hasta')

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email']

    BANEO_DIAS = 7
    UMBRAL_REPORTES = 3

    def __str__(self): return self.username
    def get_absolute_url(self): return reverse('usuarios:usuario_perfil', kwargs={'username': self.username})

    @property
    def is_baneado(self):
        """Indica si el usuario aún está en período de baneo."""
        return bool(self.baneo_hasta and timezone.now() < self.baneo_hasta)

    @property
    def tiempo_restante_baneo(self):
        """Devuelve el tiempo restante del baneo o None si no está baneado."""
        if not self.is_baneado:
            return None
        return self.baneo_hasta - timezone.now()

    def marcar_reporte_confirmado(self):
        """Marca un reporte confirmado y aplica baneo si se alcanza el umbral."""
        return self.marcar_reportes_confirmados(cantidad=1)

    def marcar_reportes_confirmados(self, cantidad=1):
        """Suma múltiples reportes confirmados y aplica baneo si se alcanza el umbral.
        
        Args:
            cantidad: Número de reportes a sumar. Si el usuario ya está baneado, no suma nada.
        
        Returns:
            True si se aplicó baneo, False en caso contrario.
        """
        if self.is_baneado:
            return False
        self.reportes_confirmados = min(self.reportes_confirmados + cantidad, self.UMBRAL_REPORTES)
        if self.reportes_confirmados >= self.UMBRAL_REPORTES:
            self.baneo_hasta = timezone.now() + datetime.timedelta(days=self.BANEO_DIAS)
            self.reportes_confirmados = 0
            self.save(update_fields=['reportes_confirmados', 'baneo_hasta'])
            return True
        self.save(update_fields=['reportes_confirmados'])
        return False

    @property
    def total_contributions(self):
        """Cuenta los guardados subidos por este usuario."""
        return self.guardados_subidos.count()

    def clean(self):
        super().clean()
        if self.avatar and hasattr(self.avatar, 'file'):
            try:
                validar_avatar(self.avatar)
            except ValidationError:
                raise

    def save(self, *args, **kwargs):
        # Controla el cambio de avatar y/o username para mantener la carpeta de perfil.
        username_anterior = None
        avatar_anterior_path = None
        avatar_anterior_name = None
        cambia_avatar = False

        if self.pk:
            try:
                ant = Usuario.objects.get(pk=self.pk)
                if ant.username != self.username:
                    username_anterior = ant.username
                if ant.avatar:
                    avatar_anterior_path = ant.avatar.path
                    avatar_anterior_name = ant.avatar.name
                # Detectar si se está subiendo un avatar nuevo
                cambia_avatar = (
                    (self.avatar and ant.avatar and self.avatar.name != ant.avatar.name) or
                    (not self.avatar and ant.avatar)
                )
            except Usuario.DoesNotExist:
                pass

        # Borrar avatar anterior solo si viene un archivo NUEVO (no el mismo ya guardado)
        if self.pk and self.avatar and hasattr(self.avatar, 'file'):
            import pathlib
            ruta_destino = pathlib.Path(settings.MEDIA_ROOT) / ruta_avatar(self, 'avatar.png')
            ruta_destino.parent.mkdir(parents=True, exist_ok=True)
            # Solo borrar si el archivo destino no es el mismo que se está guardando
            # es decir, si el avatar viene de un upload nuevo (tiene nombre corto)
            nombre_actual = getattr(self.avatar, 'name', '') or ''
            es_nuevo = not nombre_actual.startswith('perfiles/')
            try:
                if es_nuevo and ruta_destino.exists():
                    ruta_destino.unlink()
            except Exception:
                pass

        super().save(*args, **kwargs)

        if username_anterior:
            c_ant = os.path.join(settings.MEDIA_ROOT, 'perfiles', username_anterior)
            c_nue = os.path.join(settings.MEDIA_ROOT, 'perfiles', self.username)

            if cambia_avatar:
                # Cambió username Y avatar:
                # Django ya guardó el nuevo avatar en perfiles/nuevo_username/
                # Solo hay que borrar el avatar antiguo y eliminar la carpeta vieja
                if avatar_anterior_path and os.path.isfile(avatar_anterior_path):
                    os.remove(avatar_anterior_path)
                shutil.rmtree(c_ant, ignore_errors=True)
            else:
                # Solo cambió el username:
                # Mover la carpeta completa al nuevo nombre
                if os.path.isdir(c_ant):
                    shutil.move(c_ant, c_nue)
                # Actualizar ruta del avatar en BD
                if self.avatar:
                    nueva_ruta = f'perfiles/{self.username}/{os.path.basename(self.avatar.name)}'
                    Usuario.objects.filter(pk=self.pk).update(avatar=nueva_ruta)
        else:
            # Solo cambió el avatar (sin cambio de username)
            # No borrar si la ruta antigua y la nueva son el mismo archivo
            nueva_ruta = os.path.join(settings.MEDIA_ROOT, self.avatar.name) if self.avatar else None
            if cambia_avatar and avatar_anterior_path:
                try:
                    if avatar_anterior_path != nueva_ruta and os.path.isfile(avatar_anterior_path):
                        os.remove(avatar_anterior_path)
                except Exception:
                    pass

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'



from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Usuario)
def borrar_carpeta_usuario(sender, instance, **kwargs):
    """Al eliminar un usuario, borra su carpeta en media/perfiles/."""
    carpeta = os.path.join(settings.MEDIA_ROOT, 'perfiles', instance.username)
    if os.path.isdir(carpeta):
        shutil.rmtree(carpeta)
