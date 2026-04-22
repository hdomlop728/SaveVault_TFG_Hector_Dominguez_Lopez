import os, re, uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError


def ruta_guardado(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    # Usar UUID para evitar colisiones y desacoplar el nombre del archivo del nombre del usuario.
    slug = re.sub(r'[^a-z0-9]+', '_', instance.juego.titulo.lower()).strip('_') if instance.juego_id else 'desconocido'
    return f'guardados/{instance.juego.plataforma_id}/{slug}/{instance.region}/{uuid.uuid4().hex}{ext}'



def _validar_ext_basica(archivo):
    if not archivo: return
    if not os.path.splitext(archivo.name)[1]:
        raise ValidationError('El archivo debe tener extensión.')



class ArchivoGuardado(models.Model):
    OPCIONES_REGION = [('JAP','Japón'), ('USA','USA'), ('EUR','Europa')]

    juego         = models.ForeignKey('juegos.Juego', on_delete=models.CASCADE, related_name='guardados', verbose_name='Juego')
    region        = models.CharField(max_length=3, choices=OPCIONES_REGION, verbose_name='Región')
    archivo       = models.FileField(upload_to=ruta_guardado, validators=[_validar_ext_basica], verbose_name='Archivo')
    descripcion   = models.CharField(max_length=300, blank=True, verbose_name='Descripción')
    subido_por    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardados_subidos', verbose_name='Subido por')
    subido_en     = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')
    num_descargas = models.PositiveIntegerField(default=0, verbose_name='Descargas')
    activo        = models.BooleanField(default=True, verbose_name='Activo')

    def clean(self):
        super().clean()
        if self.archivo and self.juego_id:
            platform_slug = self.juego.plataforma_id
            extensiones = settings.PLATFORM_SAVE_EXTENSIONS.get(platform_slug, [])
            if extensiones:
                # Validar que la extensión del archivo coincida con las permitidas para la plataforma.
                ext = os.path.splitext(self.archivo.name)[1].lower()
                if ext not in extensiones:
                    raise ValidationError(
                        f"Extensión '{ext}' no válida para {platform_slug}. "
                        f"Permitidas: {', '.join(extensiones)}"
                    )

    def __str__(self): return f"{self.juego.titulo} [{self.region}] por {self.subido_por}"
    def get_absolute_url(self): return reverse('guardados:guardado_descargar', kwargs={'pk': self.pk})
    def increment_downloads(self):
        ArchivoGuardado.objects.filter(pk=self.pk).update(num_descargas=models.F('num_descargas') + 1)

    class Meta:
        ordering = ['-subido_en']
        verbose_name = 'Archivo de guardado'
        verbose_name_plural = 'Archivos de guardado'



from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=ArchivoGuardado)
def borrar_archivo_guardado(sender, instance, **kwargs):
    # Al borrar el registro del guardado, también eliminar el archivo físico asociado.
    if instance.archivo and os.path.isfile(instance.archivo.path):
        os.remove(instance.archivo.path)
