from django.urls import path
from . import views

app_name = 'reportes'
# Rutas para enviar reportes de guardados y comentarios.

urlpatterns = [
    path('guardado/<int:save_pk>/', views.VistaCrearReporte.as_view(), name='reporte_crear'),
    path('comentario/<int:comment_pk>/', views.VistaCrearReporteComentario.as_view(), name='reporte_comentario_crear'),
]
