# SaveVault :feelsgood:

Repositorio comunitario de archivos de guardado de videojuegos. Soporta 23 plataformas desde NES hasta PS4/Xbox One con almacenamiento seguro, búsqueda avanzada y comunidad activa.

## Características

- Explora y descarga guardados por plataforma y región (JAP / USA / EUR)
- Carrusel de portada y capturas dinámico
- Cuentas de usuario con perfiles e historial de contribuciones
- Validación de formato de guardado por plataforma
- Sistema de comentarios (requiere autenticación)
- Sistema de reportes con notificación al administrador (requiere autenticación)
- Panel de administración vía Django Admin
- Docker + Docker Compose para despliegue rápido
- CI/CD automático con GitHub Actions

---

## Tecnologías

### Backend
- **Django** 4.2 - Framework web Python
- **Python** 3.11+ - Lenguaje de programación
- **PostgreSQL** 14+ - Base de datos relacional
- **Gunicorn** 25.1.0 - Servidor WSGI de producción
- **Pillow** 12.1.1 - Procesamiento de imágenes


### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos personalizados
- **JavaScript** - Interactividad
- **Bootstrap 5** - Framework CSS
- **Cropper.js** - Edición de imágenes (avatares)

### Infraestructura
- **Docker** + **Docker Compose** - Contenedorización
- **Nginx** - Reverse proxy y servidor web
- **Let's Encrypt** + **Certbot** - Certificados SSL/TLS
- **GitHub Actions** - CI/CD automatizado
- **WhiteNoise** 6.12.0 - Servicio de archivos estáticos


### APIs Externas
- **IGDB API** - Integración con base de datos de videojuegos

---

## Inicio Rápido (Docker)

### 1. Clonar y configurar

```bash
git clone https://github.com/youruser/savevault.git
cd savevault
cp .env.example .env
# Edita .env con tus valores
```

### 2. Ejecutar con Docker Compose

```bash
docker compose up -d
```

Esto inicia:
1. Base de datos PostgreSQL
2. Ejecuta migraciones de BD
3. Carga datos iniciales (plataformas)
4. Servidor web en http://localhost:8000

### 3. Crear un superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Desarrollo Local (sin Docker)

### Requisitos
- Python 3.11+
- PostgreSQL 14+

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env
# Edita .env, establece DB_HOST=localhost y otras variables

# Ejecutar migraciones
python manage.py migrate --settings=savevault.settings.development

# Cargar datos iniciales
python manage.py loaddata fixtures/initial_data.json

# Ejecutar servidor de desarrollo
python manage.py runserver
```

---

## Pruebas

```bash
python manage.py test --settings=savevault.settings.development
```

---

## Estructura del Proyecto

```
savevault/
├── apps/                          # Aplicaciones Django (lógica de negocio)
│   ├── juegos/
│   │   ├── models.py              # Modelos de juegos
│   │   ├── api.py                 # Llamadas a IGDB API
│   │   ├── igdb.py                # Parsing de respuestas IGDB
│   │   ├── views.py               # Vistas de búsqueda y detalle
│   │   └── context_processors.py  # Menú de plataformas dinámico
│   ├── guardados/
│   │   ├── models.py              # Modelos de guardados
│   │   ├── validators.py          # Validación de archivos .sav
│   │   └── views.py               # Carga, descarga, eliminación
│   ├── usuarios/
│   │   ├── models.py              # Usuario custom con avatar
│   │   ├── middleware.py          # Bloqueo de usuarios baneados
│   │   └── views.py               # Registro, login, perfil
│   └── reportes/
│       ├── models.py              # Reportes de contenido inapropiado
│       └── views.py               # Sistema de notificaciones
├── savevault/                     # Configuración del proyecto
│   ├── settings/
│   │   ├── base.py                # Configuración común
│   │   ├── development.py         # Configuración de desarrollo
│   │   └── production.py          # Configuración de producción
│   ├── urls.py                    # Rutas principales
│   └── wsgi.py                    # Punto de entrada WSGI
├── static/
│   ├── css/                       # Estilos personalizados
│   ├── js/                        # JavaScript (Cropper.js, modales)
│   └── img/                       # Imágenes e iconos
├── templates/
│   ├── base/                      # Plantillas base (HTML)
│   ├── juegos/                    # Páginas de juegos
│   ├── guardados/                 # Páginas de guardados
│   ├── usuarios/                  # Páginas de autenticación
│   └── reportes/                  # Formulario de reportes
├── media/                         # Archivos subidos (guardados, avatares)
├── fixtures/                      # Datos iniciales (initial_data.json)
├── nginx/                         # Configuración del proxy inverso
├── certbot/                       # Certificados SSL Let's Encrypt
├── tests.py                       # Suite de pruebas
├── Dockerfile                     # Imagen Docker de la aplicación
├── docker-compose.yml             # Creacion de contenedores
└── requirements.txt               # Dependencias de Python
```

---

## Variables de Entorno

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DB_NAME` | Nombre de la base de datos PostgreSQL |
| `DB_USER` | Usuario de PostgreSQL |
| `DB_PASSWORD` | Contraseña de PostgreSQL |
| `DB_HOST` | Host de la BD |
| `ALLOWED_HOSTS` | Hosts permitidos separados por comas |
| `ADMIN_EMAIL` | Email de notificaciones del admin |
| `EMAIL_HOST` | Servidor SMTP |
| `EMAIL_PORT` | Puerto SMTP |
| `EMAIL_HOST_USER` | Email del usuario SMTP |
| `EMAIL_HOST_PASSWORD` | Contraseña SMTP |
| `IGDB_CLIENT_ID` | ID del cliente de la API IGDB |
| `IGDB_CLIENT_SECRET` | Secreto de la API IGDB |

---

## Pipeline CI/CD (GitHub Actions)

El pipeline en `.github/workflows/deploy.yml` ejecuta:

1. **Test** - Corre la suite de pruebas con PostgreSQL en paralelo
2. **Build and Push** - Construye y sube imágenes Docker:
   - App Django: `{DOCKERHUB_USERNAME}/savevault:latest`
   - Nginx: `{DOCKERHUB_USERNAME}/savevault_nginx:latest`
3. **AWS** - Copia `docker-compose.yml` al servidor AWS y levanta los servicios

### Secrets Requeridos

| Secret | Descripción |
|---|---|
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Token de Docker Hub |
| `AWS_HOSTNAME` | IP o dominio del servidor AWS |
| `AWS_USERNAME` | Usuario SSH del servidor |
| `AWS_PRIVATEKEY` | Clave privada SSH (sin passphrase) |

Se dispara automáticamente en cada push a `main`.

---

## Plataformas Soportadas y Extensiones de Guardado

| Plataforma | Extensiones Válidas |
|---|---|
| NES | `.sav` `.srm` `.fcs` `.nst` |
| SNES | `.sav` `.srm` `.zst` `.sfc` |
| GB/GBC/GBA | `.sav` `.srm` `.sgm` |
| PS1 | `.mcr` `.mcs` `.psx` `.srm` `.mc` |
| PS2 | `.ps2` `.psu` `.xps` `.max` `.cbs` |
| N64 | `.sra` `.fla` `.eep` `.mpk` `.srm` |
| ... | (ver `savevault/settings/base.py o /ayuda/ en la app desplegada`) |

---

## Notas de Seguridad

- Validación de archivos guardados por extensión por plataforma
- Imágenes de perfil limitadas a 800x800px / 5MB máximo
- Edición de avatares con Cropper.js (cliente) antes de subir
- Portadas importadas de IGDB como URLs (no almacenadas localmente)
- Protección CSRF de Django en todos los formularios
- Autenticación con usuario custom (no User genérico)
- Middleware que bloquea usuarios baneados
- Production mode: HTTPS obligatorio, SameSite cookies, SecurityMiddleware
