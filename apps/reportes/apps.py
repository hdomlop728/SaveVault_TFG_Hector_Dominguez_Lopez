from django.apps import AppConfig


# Configuración de la aplicación Reportes.
class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reportes'
    label = 'reportes'
    verbose_name = 'Reportes'
