import os, re, json, logging, uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import Juego, Plataforma, CapturaPantalla, Comentario, Genero, slugify_titulo
from .forms import FormularioComentario
from . import igdb as igdb_client
from apps.guardados.models import ArchivoGuardado
from apps.guardados.validators import validar_extension_guardado, validar_tamanio_guardado

logger = logging.getLogger(__name__)


def _igdb_entrada(igdb_id):
    """
    Recupera el detalle de un juego desde IGDB usando su identificador.
    Devuelve None si ocurre algún error de consulta.
    """
    try:
        return igdb_client.get_game_detail(int(igdb_id))
    except Exception as e:
        logger.warning('Error IGDB id=%s: %s', igdb_id, e)
        return None


def _contexto_plataforma():
    """
    Construye el contexto común para las vistas de plataformas y creación de juego.
    Incluye lista de plataformas, nombres y extensiones permitidas por plataforma.
    """
    todas = Plataforma.objects.all().order_by('nombre')
    nombres = {p.slug: p.nombre for p in todas}
    return {
        'extensiones_json': json.dumps(settings.PLATFORM_SAVE_EXTENSIONS),
        'nombres_plataformas_json': json.dumps(nombres),
        'plataformas':                [(p.slug, p.nombre) for p in todas],
    }


class VistaDetallePlataforma(View):
    template_name = 'juegos/plataformas_detalle.html'

    def get(self, request, slug):
        # Mostrar los juegos de la plataforma y aplicar búsqueda opcional.
        from django.core.paginator import Paginator
        plataforma = get_object_or_404(Plataforma, slug=slug)
        busqueda = request.GET.get('q', '').strip()
        qs = Juego.objects.filter(plataforma=plataforma).order_by('titulo')
        if busqueda:
            qs = qs.filter(titulo__icontains=busqueda)
        paginator = Paginator(qs, 24)
        page = request.GET.get('page', 1)
        juegos = paginator.get_page(page)
        return render(request, self.template_name, {
            'plataforma': plataforma,
            'juegos':     juegos,
            'busqueda':   busqueda,
        })


class VistaDetalleJuego(View):
    template_name = 'juegos/juegos_detalle.html'

    def get(self, request, pk):
        # Cargar juego y relaciones necesarias para la vista de detalle.
        juego = get_object_or_404(
            Juego.objects.select_related('plataforma','genero','creado_por').prefetch_related('capturas'), pk=pk
        )
        juego.increment_visits()

        def con_extension(qs):
            saves = list(qs)
            for s in saves:
                s.extension = os.path.splitext(s.archivo.name)[1].lower() if s.archivo else ''
            return saves

        capturas = list(juego.capturas.order_by('orden'))

        return render(request, self.template_name, {
            'juego': juego,
            'capturas': capturas,
            'region_saves': [
                ('JAP', con_extension(ArchivoGuardado.objects.filter(juego=juego, region='JAP', activo=True).select_related('subido_por')), 'Japón'),
                ('USA', con_extension(ArchivoGuardado.objects.filter(juego=juego, region='USA', activo=True).select_related('subido_por')), 'USA'),
                ('EUR', con_extension(ArchivoGuardado.objects.filter(juego=juego, region='EUR', activo=True).select_related('subido_por')), 'Europa'),
            ],
            'comentarios':     juego.comentarios.select_related('usuario').all(),
            'formulario_comentario': FormularioComentario() if request.user.is_authenticated else None,
        })

    def post(self, request, pk):
        # Guardar un comentario nuevo en el juego, si el usuario está autenticado.
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para comentar.')
            return redirect('juegos:juego_detalle', pk=pk)
        juego = get_object_or_404(Juego, pk=pk)
        form = FormularioComentario(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.juego   = juego
            c.usuario = request.user
            c.save()
            messages.success(request, 'Comentario añadido.')
        return redirect('juegos:juego_detalle', pk=pk)


class VistaCrearJuego(LoginRequiredMixin, View):
    template_name = 'juegos/juegos_crear.html'

    def get(self, request):
        # Mostrar formulario inicial rellenando el filtro de plataforma si se pasa por GET.
        ctx = {'plataforma_previa': request.GET.get('plataforma', '')}
        ctx.update(_contexto_plataforma())
        return render(request, self.template_name, ctx)

    def post(self, request):
        # Validar campos enviados y crear el juego + guardado si todo es correcto.
        errores = {}
        igdb_id       = request.POST.get('igdb_id','').strip()
        titulo        = request.POST.get('game_title','').strip()
        platform_slug = request.POST.get('game_platform','').strip()
        region        = request.POST.get('region','').strip()

        plataforma = None
        if not igdb_id or not titulo or not platform_slug:
            errores['juego'] = 'Selecciona un juego desde el buscador.'
        else:
            try:
                plataforma = Plataforma.objects.get(slug=platform_slug)
            except Plataforma.DoesNotExist:
                errores['juego'] = f'Plataforma desconocida: "{platform_slug}".'

        if not region or region not in ['JAP','USA','EUR']:
            errores['region'] = 'Selecciona una región válida.'

        archivo = request.FILES.get('file')
        if not archivo:
            errores['guardado'] = 'El archivo de guardado es obligatorio.'
        elif plataforma:
            try:
                # Validación de archivo: extensión compatible y tamaño aceptable.
                validar_extension_guardado(archivo, platform_slug, plataforma.nombre)
                validar_tamanio_guardado(archivo)
            except ValidationError as e:
                # Extraer mensaje de error limpio desde ValidationError
                if hasattr(e, 'message_list'):
                    errores['guardado'] = ' '.join(str(m) for m in e.message_list)
                elif hasattr(e, 'messages'):
                    errores['guardado'] = ' '.join(str(m) for m in e.messages)
                else:
                    errores['guardado'] = str(e)
            except Exception as e:
                errores['guardado'] = str(e)

        if not errores and plataforma:
            if Juego.objects.filter(titulo__iexact=titulo, plataforma=plataforma).exists():
                errores['juego'] = f'"{titulo}" ya existe para {plataforma.nombre}. Sube tu guardado desde la página del juego.'

        entrada = None
        if not errores and plataforma:
            entrada = _igdb_entrada(igdb_id)
            if not entrada:
                errores['juego'] = 'No se pudieron obtener los datos del juego desde IGDB. Inténtalo de nuevo.'

        if not errores and plataforma and entrada:
            genero = None
            if entrada.get('genre'):
                genero, _ = Genero.objects.get_or_create(nombre=entrada['genre'])

            juego = Juego.objects.create(
                titulo        = entrada['title'],
                descripcion   = entrada.get('description',''),
                desarrollador = entrada.get('developer',''),
                publisher     = entrada.get('publisher',''),
                num_jugadores = entrada.get('num_players', 1),
                genero        = genero,
                plataforma    = plataforma,
                creado_por    = request.user,
                portada_url   = entrada.get('cover_url',''),
            )

            # Guardar las capturas importadas de IGDB.
            for i, url in enumerate(entrada.get('screenshots',[])):
                CapturaPantalla.objects.create(juego=juego, url=url, orden=i)

            # Guardar el archivo en la ruta adecuada según plataforma, juego y región.
            ext  = os.path.splitext(archivo.name)[1]
            slug = re.sub(r'[^a-z0-9]+','_', juego.titulo.lower()).strip('_')
            path = f'guardados/{platform_slug}/{slug}/{region}/{uuid.uuid4().hex}{ext}'
            sf = ArchivoGuardado(juego=juego, region=region, descripcion=request.POST.get('description',''), subido_por=request.user)
            sf.archivo.save(path, archivo, save=False)
            sf.save()

            messages.success(request, f'"{juego.titulo}" añadido correctamente.')
            return redirect('juegos:juego_detalle', pk=juego.pk)

        ctx = {
            'errores': errores,
            'titulo_previo': titulo, 'plataforma_previa': platform_slug,
            'region_previa': region, 'igdb_id_previo': igdb_id,
        }
        ctx.update(_contexto_plataforma())
        return render(request, self.template_name, ctx)


class ListaJuegos(ListView):
    model               = Juego
    template_name       = 'juegos/juegos_lista.html'
    context_object_name = 'juegos'
    paginate_by         = 30

    def get_queryset(self):
        # Filtrar la lista de juegos por búsqueda y plataforma si se ha solicitado.
        qs = Juego.objects.select_related('plataforma').order_by('titulo')
        q    = self.request.GET.get('q','').strip()
        plat = self.request.GET.get('plataforma','').strip()
        if q:
            qs = qs.filter(Q(titulo__icontains=q)|Q(desarrollador__icontains=q))
        if plat:
            qs = qs.filter(plataforma__slug=plat)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['busqueda']      = self.request.GET.get('q','')
        ctx['plataforma_activa'] = self.request.GET.get('plataforma','')
        ctx['plataformas']       = Plataforma.objects.all().order_by('nombre')
        return ctx


class EliminarComentario(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Eliminar comentario solo si el usuario es autor o staff.
        comentario = get_object_or_404(Comentario, pk=pk)
        if comentario.usuario == request.user or request.user.is_staff:
            juego_pk = comentario.juego.pk
            comentario.delete()
            messages.success(request, 'Comentario eliminado.')
            return redirect('juegos:juego_detalle', pk=juego_pk)
        messages.error(request, 'No tienes permiso para eliminar este comentario.')
        return redirect('juegos:juego_detalle', pk=comentario.juego.pk)


