import os
from django.core.exceptions import ValidationError
from django.conf import settings


def validar_extension_guardado(archivo, platform_slug, platform_name=None):
    """Valida que el archivo tenga extensión válida para la plataforma."""
    extensiones = settings.PLATFORM_SAVE_EXTENSIONS.get(platform_slug, [])
    if not extensiones:
        return
    ext = os.path.splitext(archivo.name)[1].lower()
    if not ext:
        raise ValidationError('El archivo debe tener extensión.')
    if ext not in extensiones:
        plat_display = platform_name or platform_slug
        raise ValidationError(
            f"Extensión '{ext}' no válida para {plat_display}. "
            f"Extensiones permitidas: {', '.join(extensiones)}"
        )

def validar_tamanio_guardado(archivo, max_mb=50):
    """Valida que el archivo no supere el tamaño máximo."""
    if archivo.size > max_mb * 1024 * 1024:
        raise ValidationError(f'Archivo demasiado grande. Tamaño máximo: {max_mb} MB.')

def validar_imagen_perfil(imagen):
    """Valida tamaño y resolución del avatar."""
    from PIL import Image as PILImage
    max_size = getattr(settings, 'PROFILE_IMAGE_MAX_SIZE', 2 * 1024 * 1024)
    if imagen.size > max_size:
        raise ValidationError(f'Imagen demasiado grande. Máximo: {max_size // (1024*1024)} MB.')
    try:
        imagen.seek(0)
        img = PILImage.open(imagen)
        max_w, max_h = getattr(settings, 'PROFILE_IMAGE_MAX_RESOLUTION', (800, 800))
        if img.width > max_w or img.height > max_h:
            raise ValidationError(f'Resolución demasiado alta. Máximo: {max_w}×{max_h}px.')
        imagen.seek(0)
    except ValidationError:
        raise
    except Exception:
        raise ValidationError('No se pudo leer el archivo de imagen.')
