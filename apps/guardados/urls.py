from django.urls import path
from . import views

app_name = 'guardados'
# Rutas específicas para subir, descargar y eliminar archivos de guardado.

urlpatterns = [
    path('subir/', views.VistaSubirGuardado.as_view(), name='guardado_subir'),
    path('subir/<int:game_pk>/', views.VistaSubirGuardado.as_view(), name='guardado_subir_juego'),
    path('descargar/<int:pk>/', views.VistaDescargarGuardado.as_view(), name='guardado_descargar'),
    path('eliminar/<int:pk>/', views.VistaEliminarGuardado.as_view(), name='guardado_eliminar'),
]
