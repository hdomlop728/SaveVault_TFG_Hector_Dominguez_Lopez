from django.apps import AppConfig


# Configuración de la aplicación Usuarios.
class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    label = 'usuarios'
    verbose_name = 'Usuarios'
