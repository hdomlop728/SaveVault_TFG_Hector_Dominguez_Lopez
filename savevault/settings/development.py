"""Configuración para entorno de desarrollo con DEBUG=True y bases de datos locales."""
import os
from pathlib import Path
_env = Path(__file__).resolve().parent.parent.parent / '.env'
if _env.exists():
    with open(_env) as _f:
        for _l in _f:
            _l = _l.strip()
            if _l and not _l.startswith('#') and '=' in _l:
                _k, _, _v = _l.partition('=')
                os.environ.setdefault(_k.strip(), _v.strip())
from .base import *

# Modo de depuración: muestra errores detallados cuando algo falla.
DEBUG = True
# Aceptar requestas de cualquier host en desarrollo local.
ALLOWED_HOSTS = ['*']

# Base de datos: PostgreSQL en localhost o segun variables .env
import sys
if 'test' in sys.argv:
    # Usar SQLite para las pruebas
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    # Desactivar compresión de archivos estáticos en tests
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'savevault'),
            'USER': os.environ.get('DB_USER', 'savevault'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'savevault'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
