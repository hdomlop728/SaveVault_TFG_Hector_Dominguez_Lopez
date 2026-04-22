from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from savevault.views import VistaInicio

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', VistaInicio.as_view(), name='home'),
    path('juegos/', include('apps.juegos.urls', namespace='juegos')),
    path('guardados/', include('apps.guardados.urls', namespace='guardados')),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('reportes/', include('apps.reportes.urls', namespace='reportes')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
