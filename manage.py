#!/usr/bin/env python
import os
import sys


def main():
    # Cargar .env antes de setdefault para que DJANGO_SETTINGS_MODULE del .env tenga prioridad
    from pathlib import Path
    _env = Path(__file__).resolve().parent / '.env'
    if _env.exists():
        with open(_env) as _f:
            for _l in _f:
                _l = _l.strip()
                if _l and not _l.startswith('#') and '=' in _l:
                    _k, _, _v = _l.partition('=')
                    os.environ[_k.strip()] = _v.strip()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'savevault.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and "
            "available on your PYTHONPATH environment variable."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
