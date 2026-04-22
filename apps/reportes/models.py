from django.db import models
from django.conf import settings


class BaseReporte(models.Model):
    # Modelo abstracto común para definir campos básicos de un reporte.
    OPCIONES_ESTADO = [
        ('pending', 'Pendiente'),
        ('reviewing', 'En revisión'),
        ('resolved', 'Resuelto'),
        ('dismissed', 'Descartado'),
    ]

    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_hechos',
        verbose_name='Reportado por'
    )
    detalle = models.TextField(max_length=500, blank=True, verbose_name='Detalle')
    estado = models.CharField(
        max_length=20,
        choices=OPCIONES_ESTADO,
        default='pending',
        verbose_name='Estado'
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    resuelto_en = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de resolución')
    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_resueltos',
        verbose_name='Resuelto por'
    )

    class Meta:
        abstract = True
        ordering = ['-creado_en']
        # Ordenar los reportes más recientes primero por defecto.

    def __str__(self):
        return f"Reporte de {self.reportado_por} [{self.get_estado_display()}]"


class ReporteGuardado(BaseReporte):
    OPCIONES_MOTIVO = [
        ('broken', 'Archivo roto/corrupto'),
        ('wrong_game', 'Juego incorrecto'),
        ('malware', 'Sospechoso/Malware'),
        ('wrong_region', 'Región incorrecta'),
        ('other', 'Otro'),
    ]

    archivo_guardado = models.ForeignKey(
        'guardados.ArchivoGuardado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_guardado',
        verbose_name='Archivo de guardado'
    )
    motivo = models.CharField(max_length=20, choices=OPCIONES_MOTIVO, verbose_name='Motivo')

    class Meta:
        verbose_name = 'Reporte de guardado'
        verbose_name_plural = 'Reportes de guardados'
        unique_together = [['archivo_guardado', 'reportado_por']]
        # Un usuario solo puede reportar el mismo guardado una vez.


class ReporteComentario(BaseReporte):
    OPCIONES_MOTIVO = [
        ('spam', 'Spam o autopromoción'),
        ('abuso', 'Abuso, insultos o lenguaje inapropiado'),
        ('irrelevante', 'Irrelevante para el juego'),
        ('informacion_falsa', 'Información falsa o engañosa'),
        ('otro', 'Otro'),
    ]

    comentario = models.ForeignKey(
        'juegos.Comentario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_comentario',
        verbose_name='Comentario'
    )
    motivo = models.CharField(max_length=20, choices=OPCIONES_MOTIVO, verbose_name='Motivo')

    class Meta:
        verbose_name = 'Reporte de comentario'
        verbose_name_plural = 'Reportes de comentarios'
        unique_together = [['comentario', 'reportado_por']]
        # Un usuario solo puede reportar el mismo comentario una vez.
