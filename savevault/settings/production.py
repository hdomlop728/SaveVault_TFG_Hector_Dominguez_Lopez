"""Configuración para producción con seguridad endurecida y variables de entorno."""
import os
from pathlib import Path

# Intentar cargar .env solo si existe (para desarrollo local)
_env = Path(__file__).resolve().parent.parent.parent / '.env'
if _env.exists():
    with open(_env) as _f:
        for _l in _f:
            _l = _l.strip()
            if _l and not _l.startswith('#') and '=' in _l:
                _k, _, _v = _l.partition('=')
                os.environ.setdefault(_k.strip(), _v.strip())

from .base import *

# DEBUG apagado: no mostrar información sensible en errores.
DEBUG = False

# Solo se aceptan hosts en ALLOWED_HOSTS (especificado en .env)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Orígenes de confianza para CSRF
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://savevault.freemyip.com'
).split(',')

# Confiar en el header X-Forwarded-Proto que manda nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Base de datos: conectarse a la base de datos especificada en variables de entorno.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'savevault'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'admin'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Protecciones de seguridad para navegadores y clientes.
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Cookies seguras — activadas porque tenemos SSL real
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configuración de correo electrónico para envíar notificaciones y recuperación de contraseña.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
