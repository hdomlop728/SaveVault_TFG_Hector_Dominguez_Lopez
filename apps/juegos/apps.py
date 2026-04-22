from django.apps import AppConfig


# Configuración de la aplicación Juegos.
class JuegosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.juegos'
    label = 'juegos'
    verbose_name = 'Juegos'
