from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'usuarios'
# Rutas para registro, login, perfil, edición, eliminación y estado de baneo.

urlpatterns = [
    path('registro/', views.VistaRegistro.as_view(), name='usuario_registro'),
    path('acceder/', views.VistaLogin.as_view(), name='usuario_acceder'),
    path('salir/', LogoutView.as_view(), name='usuario_salir'),
    path('perfil/<str:username>/', views.VistaPerfil.as_view(), name='usuario_perfil'),
    path('editar/', views.VistaEditarPerfil.as_view(), name='usuario_editar'),
    path('eliminar-cuenta/', views.VistaEliminarCuenta.as_view(), name='usuario_eliminar'),
    path('baneado/', views.VistaBaneado.as_view(), name='usuario_baneado'),
]
