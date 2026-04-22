import json, os
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import FileResponse, Http404
from django.conf import settings

from .models import ArchivoGuardado
from .forms import FormularioGuardado
from apps.juegos.models import Juego


class VistaSubirGuardado(LoginRequiredMixin, View):
    template_name = 'guardados/guardados_subir.html'

    def get(self, request, game_pk=None):
        # Mostrar el formulario de subida de guardado, con opción de juego preseleccionado.
        juego = get_object_or_404(Juego, pk=game_pk) if game_pk else None
        form  = FormularioGuardado(juego=juego)
        return render(request, self.template_name, {
            'form': form, 'juego': juego,
            'extensiones_json': json.dumps(settings.PLATFORM_SAVE_EXTENSIONS),
        })

    def post(self, request, game_pk=None):
        # Procesar la subida de un nuevo archivo de guardado.
        juego = get_object_or_404(Juego, pk=game_pk) if game_pk else None
        form  = FormularioGuardado(request.POST, request.FILES, juego=juego)
        if form.is_valid():
            guardado = form.save(commit=False)
            # No guardar el usuario en el formulario, lo asignamos desde la sesión.
            guardado.subido_por = request.user
            if juego:
                guardado.juego = juego
            guardado.save()
            messages.success(request, 'Archivo de guardado subido correctamente.')
            return redirect('juegos:juego_detalle', pk=guardado.juego.pk)
        return render(request, self.template_name, {
            'form': form, 'juego': juego,
            'extensiones_json': json.dumps(settings.PLATFORM_SAVE_EXTENSIONS),
        })


class VistaDescargarGuardado(View):
    def get(self, request, pk):
        # Descargar el archivo de guardado asociado si existe y está activo.
        guardado = get_object_or_404(ArchivoGuardado, pk=pk, activo=True)
        if not guardado.archivo:
            raise Http404('Archivo no encontrado.')
        guardado.increment_downloads()
        ruta = guardado.archivo.path
        if not os.path.exists(ruta):
            raise Http404('Archivo no encontrado en el servidor.')
        ext = os.path.splitext(ruta)[1]
        if not ext:
            dot = guardado.archivo.name.rfind('.')
            ext = guardado.archivo.name[dot:] if dot != -1 else ''
        titulo  = guardado.juego.titulo.replace(' ','_')
        usuario = guardado.subido_por.username
        region  = guardado.region
        nombre_descarga = f'{titulo}_{usuario}_({region}){ext}'
        return FileResponse(open(ruta,'rb'), as_attachment=True, filename=nombre_descarga)


class VistaEliminarGuardado(LoginRequiredMixin, View):
    template_name = 'guardados/guardado_eliminar.html'

    def get(self, request, pk):
        # Mostrar confirmación antes de borrar el guardado.
        guardado = get_object_or_404(ArchivoGuardado, pk=pk)
        if guardado.subido_por != request.user and not request.user.is_staff:
            messages.error(request, 'No tienes permiso para realizar esta acción.')
            return redirect('juegos:juego_detalle', pk=guardado.juego.pk)
        return render(request, self.template_name, {
            'guardado': guardado,
        })

    def post(self, request, pk):
        # Borrar el guardado tanto de disco como de la base de datos.
        guardado = get_object_or_404(ArchivoGuardado, pk=pk)
        if guardado.subido_por == request.user or request.user.is_staff:
            juego_pk = guardado.juego.pk
            if guardado.archivo and os.path.isfile(guardado.archivo.path):
                # Eliminar el archivo físico antes de borrar el registro.
                os.remove(guardado.archivo.path)
            guardado.delete()
            messages.success(request, 'Archivo de guardado eliminado.')
            return redirect('juegos:juego_detalle', pk=juego_pk)
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('juegos:juego_detalle', pk=guardado.juego.pk)

