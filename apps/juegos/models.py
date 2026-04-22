import re, os
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError


def slugify_titulo(titulo):
    """Genera un slug seguro a partir del título de un juego."""
    return re.sub(r'[^a-z0-9]+', '_', titulo.lower()).strip('_')



class Plataforma(models.Model):
    """Modelo para representar plataformas y consolas compatibles."""
    OPCIONES_PLATAFORMA = [
        ('NES','NES'), ('MASTER_SYSTEM','Master System'), ('GB','Game Boy'),
        ('GAME_GEAR','Game Gear'), ('SNES','SNES'), ('MEGADRIVE','Megadrive'),
        ('PS1','PlayStation 1'), ('SEGA_SATURN','Sega Saturn'), ('N64','Nintendo 64'),
        ('GBC','Game Boy Color'), ('GBA','Game Boy Advance'), ('GAME_CUBE','GameCube'),
        ('PS2','PlayStation 2'), ('XBOX','Xbox'), ('XBOX_360','Xbox 360'), ('PSP','PSP'),
        ('PS3','PlayStation 3'), ('NDS','Nintendo DS'), ('WII','Wii'), ('WIIU','Wii U'),
        ('NINTENDO_3DS','Nintendo 3DS'), ('PS4','PlayStation 4'), ('XBOX_ONE','Xbox One'),
    ]
    slug   = models.CharField(max_length=20, choices=OPCIONES_PLATAFORMA, unique=True, primary_key=True)
    nombre = models.CharField(max_length=50, editable=False)

    def save(self, *args, **kwargs):
        # Guardar siempre el nombre legible correspondiente al slug seleccionado.
        self.nombre = dict(self.OPCIONES_PLATAFORMA).get(self.slug, self.slug)
        super().save(*args, **kwargs)

    def __str__(self): return self.nombre
    def get_absolute_url(self): return reverse('juegos:plataforma_detalle', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Plataforma'
        verbose_name_plural = 'Plataformas'



class Genero(models.Model):
    """Modelo de género de juego para clasificar títulos."""
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre')

    def __str__(self): return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'



class Juego(models.Model):
    """Modelo principal de juego con datos importados de IGDB."""
    titulo        = models.CharField(max_length=200, verbose_name='Título')
    descripcion   = models.TextField(blank=True, verbose_name='Descripción')
    desarrollador = models.CharField(max_length=100, blank=True, verbose_name='Desarrollador')
    publisher     = models.CharField(max_length=100, blank=True, verbose_name='Publicador')
    num_jugadores = models.PositiveSmallIntegerField(default=1, verbose_name='Jugadores')
    genero        = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True, related_name='juegos', verbose_name='Género')
    plataforma    = models.ForeignKey(Plataforma, on_delete=models.CASCADE, related_name='juegos', verbose_name='Plataforma')
    creado_por    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='juegos_creados', verbose_name='Creado por')
    creado_en     = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    visitas       = models.PositiveIntegerField(default=0, verbose_name='Visitas')
    # URL de portada importada de IGDB — no se sube archivo
    portada_url   = models.URLField(max_length=500, blank=True, verbose_name='URL de portada (IGDB)')

    def __str__(self): return f"{self.titulo} ({self.plataforma})"
    def get_absolute_url(self): return reverse('juegos:juego_detalle', kwargs={'pk': self.pk})
    def increment_visits(self):
        # Incrementa el contador de visitas en la base de datos sin cargar el objeto completo.
        Juego.objects.filter(pk=self.pk).update(visitas=models.F('visitas') + 1)

    class Meta:
        ordering = ['titulo']
        unique_together = ['titulo', 'plataforma']
        verbose_name = 'Juego'
        verbose_name_plural = 'Juegos'



class CapturaPantalla(models.Model):
    """Captura de pantalla importada desde IGDB. Se guarda solo la URL."""
    juego   = models.ForeignKey(Juego, on_delete=models.CASCADE, related_name='capturas')
    url     = models.URLField(max_length=500)
    orden   = models.PositiveSmallIntegerField(default=0)
    añadido = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'añadido']
        verbose_name = 'Captura de pantalla'
        verbose_name_plural = 'Capturas de pantalla'

    def __str__(self): return f'Captura {self.orden} de {self.juego.titulo}'



class Comentario(models.Model):
    """Comentario de usuario asociado a un juego."""
    juego      = models.ForeignKey(Juego, on_delete=models.CASCADE, related_name='comentarios')
    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comentarios')
    texto      = models.TextField(max_length=1000, verbose_name='Comentario')
    creado_en  = models.DateTimeField(auto_now_add=True)
    editado_en = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Comentario de {self.usuario} en {self.juego}"

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

