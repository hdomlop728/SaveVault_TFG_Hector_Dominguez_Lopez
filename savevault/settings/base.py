"""Configuración base común a todos los entornos (desarrollo, producción)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-changeme-in-production')

# Aplicaciones instaladas: modulos Django contrib + aplicaciones propias del proyecto.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Aplicaciones locales: cada modulo maneja su logica de negocio
    'apps.usuarios',  # Usuarios, autenticacion y perfiles
    'apps.juegos',    # Catalogo de juegos e importacion desde IGDB
    'apps.guardados', # Gestion de archivos de juego guardados
    'apps.reportes',  # Sistema de reportes de contenido inapropiado
]

# Middleware procesa cada request: seguridad, sesiones, CSRF, auth, mensajes, XFrame
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Sirve archivos estaticos optimizados
    'django.contrib.sessions.middleware.SessionMiddleware',  # Gestiona sesiones de usuario
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Proteccion contra ataques CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Carga usuario autenticado
    'apps.usuarios.middleware.BaneoMiddleware',  # Bloquea usuarios baneados
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Proteccion X-Frame-Options
]

ROOT_URLCONF = 'savevault.urls'

# Renderizador de plantillas: busca archivos en templates/ y subdirectorios de apps
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Archivos .html globales del proyecto
        'APP_DIRS': True,  # Busca plantillas dentro de cada aplicacion
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',  # Pasa usuario a plantillas
                'django.contrib.messages.context_processors.messages',  # Pasa mensajes flash
                'apps.juegos.context_processors.plataformas_menu',  # Menu de plataformas personalizado
            ],
        },
    },
]

WSGI_APPLICATION = 'savevault.wsgi.application'

# ── Validacion de contrasenas ────────────────────────────────────────────────
# Valida contrasenas contra diccionarios comunes y patrones debiles cuando se registra usuario
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # No igual a username
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},  # Longitud minima
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},  # No las 10k+ comunes
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},  # No solo numeros
]

# ── Internacionalizacion ────────────────────────────────────────────────────
# Configuracion de idioma y zona horaria del servidor y base de datos
LANGUAGE_CODE = 'es-es'  # Espanol de Espana
TIME_ZONE = 'Europe/Madrid'  # Zona horaria peninsular
USE_I18N = True  # Activa sistema de internacionalizacion
USE_TZ = True  # Almacena fechas en UTC, convierte al mostrar

# ── Archivos estaticos ──────────────────────────────────────────────────────
# WhiteNoise comprime estaticos (CSS, JS, IMG) y les anade hash para cache indefinido en prod
STATIC_URL = '/static/'  # URL publica para servir CSS, JS, imagenes
STATICFILES_DIRS = [BASE_DIR / 'static']  # Carpeta fuente de archivos estaticos
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Carpeta de salida tras collectstatic
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # Compresion inteligente

# ── Archivos de media (subidos por usuarios) ─────────────────────────────────
# Guardados de juegos (.sav), avatares de perfil y otros archivos enviados por usuarios
MEDIA_URL = '/media/'  # URL publica para acceder a archivos de usuarios
MEDIA_ROOT = BASE_DIR / 'media'  # Carpeta del servidor donde se almacenan

# ── Base de datos ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Autenticacion ───────────────────────────────────────────────────────────
# Implementacion personalizada: Usuario con avatar, perfil expandido y estado de baneo
AUTH_USER_MODEL = 'usuarios.Usuario'  # Modelo custom en lugar del User generico
LOGIN_URL = '/usuarios/acceder/'  # Redirige aqui si acceso requiere login
LOGIN_REDIRECT_URL = '/'  # Destino tras login exitoso
LOGOUT_REDIRECT_URL = '/'  # Destino tras logout

# ── Avatares de perfil ──────────────────────────────────────────────────────
# Validacion de imagenes subidas: tamaño y resolucion maximos para evitar sobrecarga
PROFILE_IMAGE_MAX_SIZE = 5 * 1024 * 1024  # 5 MB maximo (PNG 800x800 suele ocupar ~2-3 MB)
PROFILE_IMAGE_MAX_RESOLUTION = (800, 800)  # Redimensiona a 800x800px si supera

# ── IGDB ──────────────────────────────────────────────────────────────────────
# Credenciales de la API de IGDB para importar datos de juegos
# Obtenerlas en: https://dev.twitch.tv/console/apps
IGDB_CLIENT_ID     = os.environ.get('IGDB_CLIENT_ID', '')
IGDB_CLIENT_SECRET = os.environ.get('IGDB_CLIENT_SECRET', '')

IGDB_TRANSLATE_TO_SPANISH = os.environ.get('IGDB_TRANSLATE_TO_SPANISH', '1').lower() not in ('0', 'false', 'no')
IGDB_TRANSLATE_PROVIDER = os.environ.get('IGDB_TRANSLATE_PROVIDER', 'google').lower()
IGDB_TRANSLATE_URL = os.environ.get('IGDB_TRANSLATE_URL', 'https://translate.googleapis.com/translate_a/single')

# ── Extensiones de archivo validas por plataforma ──────────────────────────
# Define que tipos de archivo de guardado acepta cada consola para evitar subidas maliciosas
PLATFORM_SAVE_EXTENSIONS = {
    'NES': ['.sav', '.srm', '.fcs', '.nst'],
    'MASTER_SYSTEM': ['.sav', '.srm', '.ssv'],
    'GB': ['.sav', '.srm', '.sgm'],
    'GAME_GEAR': ['.sav', '.srm', '.gg'],
    'SNES': ['.sav', '.srm', '.zst', '.sfc'],
    'MEGADRIVE': ['.sav', '.srm', '.md', '.gen'],
    'PS1': ['.mcr', '.mcs', '.psx', '.srm', '.mc'],
    'SEGA_SATURN': ['.bkr', '.sat'],
    'N64': ['.sra', '.fla', '.eep', '.mpk', '.srm'],
    'GBC': ['.sav', '.srm', '.sgm'],
    'GBA': ['.sav', '.srm', '.sgm'],
    'GAME_CUBE': ['.gci', '.raw', '.gcz'],
    'PS2': ['.ps2', '.psu', '.xps', '.max', '.cbs'],
    'XBOX': ['.sav', '.xsv'],
    'XBOX_360': ['.sav', '.xsv', '.con'],
    'PSP': ['.vmp', '.bin', '.mdf'],
    'PS3': ['.psv', '.bin', '.sfo'],
    'NDS': ['.sav', '.dsv', '.nds'],
    'WII': ['.sav', '.bin', '.dat'],
    'WIIU': ['.sav', '.bin'],
    'NINTENDO_3DS': ['.sav', '.bin', '.cfg'],
    'PS4': ['.bin', '.psv'],
    'XBOX_ONE': ['.sav', '.bin'],
}

# ── Correo electronico ──────────────────────────────────────────────────────
# En desarrollo se imprime en consola; en produccion SMTP real envia desde production.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Console para desarrollo
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@savevault.com')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@savevault.com')
