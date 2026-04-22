"""
Cliente de la API de IGDB para SaveVault.

Las credenciales se configuran en .env:
    IGDB_CLIENT_ID=your_client_id
    IGDB_CLIENT_SECRET=your_client_secret

Obténlas en: https://dev.twitch.tv/console/apps
  - Crea una app, categoría "Other", URL de redirección http://localhost
  - Copia el Client ID y genera un Client Secret
"""
import time
import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Código de idioma español para las traducciones de IGDB.
# IGDB puede devolver cadenas traducidas si se especifica un idioma.
IGDB_LANGUAGE_SPANISH = 6

# ── Mapa de IDs de plataforma de IGDB (ID numérico de IGDB → nuestro slug) ──
IGDB_PLATFORM_MAP = {
    18:  'NES',
    35:  'MASTER_SYSTEM',
    33:  'GB',
    26:  'GAME_GEAR',
    19:  'SNES',
    29:  'MEGADRIVE',
    7:   'PS1',
    32:  'SEGA_SATURN',
    4:   'N64',
    22:  'GBC',
    24:  'GBA',
    21:  'GAME_CUBE',
    8:   'PS2',
    11:  'XBOX',
    12:  'XBOX_360',
    38:  'PSP',
    9:   'PS3',
    5:   'WII',
    41:  'NDS',
    23:  'WIIU',
    37:  'NINTENDO_3DS',
    48:  'PS4',
    49:  'XBOX_ONE',
}
# Inverso: nuestro slug → ID de IGDB (para filtrar búsquedas por plataforma)
SLUG_TO_IGDB = {v: k for k, v in IGDB_PLATFORM_MAP.items()}


def _get_token():
    """
    Obtiene un token de OAuth válido de Twitch, en caché hasta 10 minutos antes de expirar.
    Los tokens de IGDB duran alrededor de 60 días; aquí se renueva automáticamente.
    """
    cached = cache.get('igdb_token')
    if cached:
        return cached

    client_id     = getattr(settings, 'IGDB_CLIENT_ID', '')
    client_secret = getattr(settings, 'IGDB_CLIENT_SECRET', '')

    if not client_id or not client_secret:
        raise ValueError(
            'IGDB_CLIENT_ID and IGDB_CLIENT_SECRET must be set in your .env file.\n'
            'Get them at https://dev.twitch.tv/console/apps'
        )

    resp = requests.post(
        'https://id.twitch.tv/oauth2/token',
        params={
            'client_id':     client_id,
            'client_secret': client_secret,
            'grant_type':    'client_credentials',
        },
        timeout=10,
    )
    resp.raise_for_status()
    data       = resp.json()
    token      = data['access_token']
    expires_in = data.get('expires_in', 3600)

    # Guardar token en caché con un margen de seguridad de 10 minutos.
    cache.set('igdb_token', token, timeout=max(expires_in - 600, 60))
    return token


def _headers():
    return {
        'Client-ID':     settings.IGDB_CLIENT_ID,
        'Authorization': f'Bearer {_get_token()}',
        'Accept':        'application/json',
        'Content-Type':  'text/plain',
    }


def _escape_query(value):
    return value.replace('\\', '\\\\').replace('"', '\\"')


def _translate_text(text, target_language='es'):
    if not text or not getattr(settings, 'IGDB_TRANSLATE_TO_SPANISH', False):
        return text

    provider = getattr(settings, 'IGDB_TRANSLATE_PROVIDER', 'google').lower()
    if provider != 'google':
        return text

    url = getattr(settings, 'IGDB_TRANSLATE_URL', 'https://translate.googleapis.com/translate_a/single')
    try:
        resp = requests.get(
            url,
            params={
                'client': 'gtx',
                'sl': 'en',
                'tl': target_language,
                'dt': 't',
                'q': text,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and isinstance(data[0], list):
            return ''.join(item[0] for item in data[0] if item and item[0])
    except Exception as e:
        logger.warning('IGDB translation failed: %s', e)
    return text


def _post(endpoint, body):
    """Envía una petición POST a un endpoint de IGDB y devuelve el JSON parseado."""
    url  = f'https://api.igdb.com/v4/{endpoint}'
    body = body.strip()
    resp = requests.post(url, headers=_headers(), data=body, timeout=10)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error('IGDB request failed (%s): %s\n%s', url, resp.text, body)
        raise
    return resp.json()


# ── API pública ───────────────────────────────────────────────────────────────

def search_games(query, platform_slug=None, limit=30):
    """
    Busca juegos por nombre en IGDB, con filtro opcional por plataforma.
    Devuelve una lista de dicts: {igdb_id, title, platform_slug, cover_url, year}
    """
    platform_filter = ''
    if platform_slug and platform_slug in SLUG_TO_IGDB:
        igdb_id = SLUG_TO_IGDB[platform_slug]
        platform_filter = f'where platforms = ({igdb_id});'

    escaped_query = _escape_query(query)
    if platform_filter:
        body = f'''
            search "{escaped_query}";
            fields name, platforms, cover.url, first_release_date;
            {platform_filter}
            limit {limit};
        '''
    else:
        body = f'''
            search "{escaped_query}";
            fields name, platforms, cover.url, first_release_date;
            limit {limit};
        '''

    try:
        results = _post('games', body)
    except Exception as e:
        logger.warning('IGDB search error: %s', e)
        return []

    games = []
    for g in results:
        # Mapear IDs de plataforma de IGDB a nuestros slugs (tomar la primera coincidencia).
        slug = None
        for pid in g.get('platforms', []):
            if pid in IGDB_PLATFORM_MAP:
                # Preferir la plataforma solicitada si hay varias coincidencias.
                candidate = IGDB_PLATFORM_MAP[pid]
                if platform_slug and candidate == platform_slug:
                    slug = candidate
                    break
                if slug is None:
                    slug = candidate

        if not slug:
            continue  # plataforma no disponible en nuestro sistema

        cover_url = None
        if g.get('cover') and g['cover'].get('url'):
            # Usar t_cover_big para obtener una portada de mayor tamaño.
            cover_url = g['cover']['url'].replace('t_thumb', 't_cover_big')
            if cover_url.startswith('//'):
                cover_url = 'https:' + cover_url

        year = None
        if g.get('first_release_date'):
            year = time.strftime('%Y', time.gmtime(g['first_release_date']))

        games.append({
            'igdb_id':    g['id'],
            'title':      g['name'],
            'platform':   slug,
            'cover_url':  cover_url,
            'year':       year,
        })

    return games


def get_game_detail(igdb_id):
    """
    Recupera el detalle completo de un juego desde IGDB a partir de su ID.
    Devuelve un diccionario con los campos que necesita SaveVault.
    """
    body = f'''
        fields
            name,
            summary,
            storyline,
            involved_companies.company.name,
            involved_companies.developer,
            involved_companies.publisher,
            genres.name,
            platforms,
            cover.url,
            screenshots.url,
            first_release_date,
            game_modes.name,
            multiplayer_modes.onlinemax,
            multiplayer_modes.offlinemax,
            rating,
            aggregated_rating;
        where id = {igdb_id};
        limit 1;
    '''

    try:
        results = _post('games', body)
    except Exception as e:
        logger.warning('IGDB detail error: %s', e)
        return None

    if not results:
        return None

    g = results[0]

    # Desarrollador / publicador
    developer = ''
    publisher = ''
    for ic in g.get('involved_companies', []):
        company_name = ic.get('company', {}).get('name', '')
        if ic.get('developer') and not developer:
            developer = company_name
        if ic.get('publisher') and not publisher:
            publisher = company_name

    # Género (primer resultado disponible)
    genre = ''
    if g.get('genres'):
        genre = g['genres'][0]['name']

    # URL de portada — usar t_cover_big para portada de mayor tamaño.
    cover_url = None
    if g.get('cover') and g['cover'].get('url'):
        cover_url = g['cover']['url'].replace('t_thumb', 't_cover_big')
        if cover_url.startswith('//'):
            cover_url = 'https:' + cover_url

    # Capturas de pantalla — usar t_screenshot_big y limitar a 6.
    screenshots = []
    for s in g.get('screenshots', [])[:6]:
        url = s.get('url', '').replace('t_thumb', 't_screenshot_big')
        if url.startswith('//'):
            url = 'https:' + url
        if url:
            screenshots.append(url)

    # Año de lanzamiento
    year = None
    if g.get('first_release_date'):
        year = time.strftime('%Y', time.gmtime(g['first_release_date']))

    # Jugadores estimados a partir de los modos multijugador.
    num_players = 1
    for mm in g.get('multiplayer_modes', []):
        candidates = [mm.get('offlinemax', 1), mm.get('onlinemax', 1)]
        num_players = max(num_players, max(c for c in candidates if c))

    # Primer slug de plataforma coincidente en nuestro mapeo.
    platform_slug = None
    for pid in g.get('platforms', []):
        if pid in IGDB_PLATFORM_MAP:
            platform_slug = IGDB_PLATFORM_MAP[pid]
            break

    description = g.get('summary') or g.get('storyline') or ''
    if description:
        description = _translate_text(description)

    return {
        'igdb_id':      g['id'],
        'title':        g['name'],
        'description':  description,
        'developer':    developer,
        'publisher':    publisher,
        'genre':        genre,
        'year':         year,
        'num_players':  num_players,
        'platform':     platform_slug,
        'cover_url':    cover_url,
        'screenshots':  screenshots,
    }
