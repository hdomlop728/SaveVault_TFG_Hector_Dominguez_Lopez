import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from . import igdb as igdb_client
from .models import Juego

logger = logging.getLogger(__name__)


@require_GET
def api_games_list(request):
    """
    GET /games/api/games/?q=mario&platform=NES
    Búsqueda en vivo en IGDB. Devuelve hasta 30 resultados.
    """
    query = request.GET.get('q', '').strip()
    platform_slug = request.GET.get('platform', '').strip() or None

    # Evitar consultas demasiado cortas que generan resultados poco útiles.
    if len(query) < 2:
        return JsonResponse({'games': []})

    try:
        results = igdb_client.search_games(query, platform_slug=platform_slug, limit=30)
    except ValueError as e:
        # Error de configuración: faltan credenciales IGDB.
        return JsonResponse({'error': str(e), 'games': []}, status=503)
    except Exception as e:
        logger.error('IGDB search failed: %s', e)
        # Error genérico al consultar IGDB.
        return JsonResponse({'error': 'Búsqueda no disponible', 'games': []}, status=503)

    return JsonResponse({'games': results})


@require_GET
def api_game_detail(request):
    """
    GET /games/api/game/?igdb_id=1234
    Detalle completo de un juego a partir de su ID de IGDB.
    """
    igdb_id = request.GET.get('igdb_id', '').strip()

    if not igdb_id:
        # El identificador es obligatorio para esta consulta.
        return JsonResponse({'error': 'igdb_id obligatorio'}, status=400)

    try:
        detail = igdb_client.get_game_detail(int(igdb_id))
    except Exception as e:
        logger.error('IGDB detail failed: %s', e)
        # Falla al recuperar los detalles del juego.
        return JsonResponse({'error': 'Detalle no disponible'}, status=503)

    if not detail:
        # Juego no encontrado en IGDB.
        return JsonResponse({'error': 'Juego no encontrado'}, status=404)

    return JsonResponse({'game': detail})


@require_GET
def api_buscar_local(request):
    """
    GET /juegos/api/buscar/?q=mario
    Búsqueda en tiempo real sobre los juegos almacenados en la base de datos local.
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'resultados': []})

    plataforma = request.GET.get('plataforma', '').strip()
    # Filtrar por plataforma solo si se proporciona un slug válido.
    qs = Juego.objects.filter(titulo__icontains=q).select_related('plataforma')
    if plataforma:
        # Filtrar por plataforma solo si se indica.
        qs = qs.filter(plataforma__slug=plataforma)
    juegos = qs.order_by('titulo')[:8]

    resultados = [{
        'pk':        j.pk,
        'titulo':    j.titulo,
        'plataforma': j.plataforma.nombre,
        'portada':   j.portada_url or '',
        'url':       j.get_absolute_url(),
    } for j in juegos]

    return JsonResponse({'resultados': resultados})
