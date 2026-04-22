from django.apps import AppConfig


# Configuración de la aplicación Guardados.
class GuardadosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.guardados'
    label = 'guardados'
    verbose_name = 'Guardados'
