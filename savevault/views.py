"""Vistas raíz del proyecto: página de inicio y página de ayuda."""
from django.views import View
from django.shortcuts import render
from django.conf import settings

from apps.juegos.models import Juego
from apps.guardados.models import ArchivoGuardado


class VistaAyuda(View):
    """Página de ayuda con FAQ y tabla de formatos de guardado por plataforma."""
    template_name = 'base/ayuda.html'

    def get(self, request):
        from apps.juegos.models import Plataforma

        faq = [
            ('¿Es gratuito usar SaveVault?', 'Sí, SaveVault es completamente gratuito. Solo necesitas crear una cuenta para subir y descargar archivos de guardado.'),
            ('¿Qué tamaño máximo tiene un archivo de guardado?', 'El tamaño máximo permitido por archivo es de 50 MB.'),
            ('¿Puedo subir guardados de cualquier plataforma?', 'Puedes subir guardados de todas las plataformas disponibles en SaveVault. Consulta la tabla de formatos al final de esta página para ver los tipos de archivo aceptados por cada plataforma.'),
            ('¿Por qué no aparece el juego que busco?', 'Si el juego no está en la base de datos, puedes añadirlo tú mismo desde la sección Juegos haciendo clic en Añadir juego. Los datos se importan automáticamente desde IGDB.'),
            ('¿Puedo editar o actualizar un guardado ya subido?', 'Actualmente no es posible editar un guardado existente. Si necesitas actualizarlo, elimina el anterior y sube el nuevo.'),
            ('¿Qué hago si un guardado descargado no funciona?', 'Primero verifica que el formato del archivo sea compatible con tu emulador. Si el problema persiste, usa el botón de reporte para notificarlo al administrador.'),
            ('¿Mis datos están seguros?', 'Sí. Las contraseñas se almacenan cifradas y nunca compartimos tu información personal con terceros.'),
            ('¿Cómo puedo eliminar mi cuenta?', 'Ve a tu perfil desde el menú de usuario y encontrarás el botón Eliminar cuenta.'),
        ]

        plataformas = settings.PLATFORM_SAVE_EXTENSIONS
        nombres = {p.slug: p.nombre for p in Plataforma.objects.all()}
        formatos = [(nombres.get(slug, slug), exts) for slug, exts in plataformas.items()]

        return render(request, self.template_name, {
            'faq': faq,
            'formatos_plataforma': formatos,
        })

class VistaInicio(View):
    """Página de inicio mostrando los juegos más visitados y guardados recientes."""
    template_name = 'base/home.html'

    def get(self, request):
        return render(request, self.template_name, {
            'top_juegos': Juego.objects.select_related('plataforma').order_by('-visitas')[:5],
            'guardados_recientes': ArchivoGuardado.objects.filter(activo=True).select_related('juego', 'subido_por').order_by('-subido_en')[:10],
        })
