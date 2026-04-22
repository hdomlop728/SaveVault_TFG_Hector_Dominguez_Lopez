from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from savevault.views import VistaAyuda, VistaInicio

urlpatterns = [
    path('admin/', admin.site.urls),  # Panel administrativo de Django
    path('', VistaInicio.as_view(), name='home'),  # Pagina principal
    path('ayuda/', VistaAyuda.as_view(), name='ayuda'),  # Pagina de ayuda
    path('juegos/', include('apps.juegos.urls', namespace='juegos')),  # URLs de juegos
    path('guardados/', include('apps.guardados.urls', namespace='guardados')),  # URLs de guardados
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),  # URLs de usuarios
    path('reportes/', include('apps.reportes.urls', namespace='reportes')),  # URLs de reportes
]

# Servir archivos subidos por usuarios: avatares, guardados de juegos, etc.
# En desarrollo tambien sirve archivos estaticos (CSS, JS) si no esta configurado WhiteNoise
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
if settings.DEBUG:
    # En desarrollo, Django sirve archivos estaticos automaticamente
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ── Paginas de error personalizadas ──────────────────────────────────────────
# Django las usa automaticamente cuando DEBUG=False en produccion
# Las plantillas correspondientes estan en templates/400.html, 403.html, 404.html, 500.html
handler400 = 'django.views.defaults.bad_request'  # Solicitud malformada
handler403 = 'django.views.defaults.permission_denied'  # Acceso denegado (perms)
handler404 = 'django.views.defaults.page_not_found'  # URL no encontrada
handler500 = 'django.views.defaults.server_error'  # Error interno del servidor
