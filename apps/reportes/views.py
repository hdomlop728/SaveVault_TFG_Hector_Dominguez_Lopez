from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import ReporteComentario, ReporteGuardado
from .forms import FormularioReporteComentario, FormularioReporteGuardado
from apps.guardados.models import ArchivoGuardado
from apps.juegos.models import Comentario


class VistaCrearReporte(LoginRequiredMixin, View):
    template_name = 'reportes/reportes_crear.html'

    def get(self, request, save_pk):
        guardado = get_object_or_404(ArchivoGuardado, pk=save_pk, activo=True)
        if ReporteGuardado.objects.filter(archivo_guardado=guardado, reportado_por=request.user).exists():
            messages.warning(request, 'Ya has reportado este archivo de guardado.')
            return redirect('juegos:juego_detalle', pk=guardado.juego.pk)
        return render(request, self.template_name, {'form': FormularioReporteGuardado(), 'guardado': guardado})

    def post(self, request, save_pk):
        guardado = get_object_or_404(ArchivoGuardado, pk=save_pk, activo=True)
        # Prevenir reportes duplicados del mismo usuario sobre el mismo guardado.
        if ReporteGuardado.objects.filter(archivo_guardado=guardado, reportado_por=request.user).exists():
            messages.warning(request, 'Ya has reportado este archivo de guardado.')
            return redirect('juegos:juego_detalle', pk=guardado.juego.pk)

        form = FormularioReporteGuardado(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.archivo_guardado = guardado
            reporte.reportado_por = request.user
            reporte.save()
            try:
                send_mail(
                    subject=f'[SaveVault] Nuevo reporte sobre: {guardado.juego.titulo}',
                    message=(
                        f'Se ha reportado un archivo de guardado.\n\n'
                        f'Juego: {guardado.juego.titulo} ({guardado.juego.plataforma})\n'
                        f'Región: {guardado.region}\n'
                        f'Subido por: {guardado.subido_por}\n'
                        f'Reportado por: {request.user}\n'
                        f'Motivo: {reporte.get_motivo_display()}\n'
                        f'Detalle: {reporte.detalle}\n\n'
                        f'Por favor, revísalo en el panel de administración.'
                    ),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@savevault.com'),
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Reporte enviado. Gracias por ayudar a mantener SaveVault limpio.')
            return redirect('juegos:juego_detalle', pk=guardado.juego.pk)

        return render(request, self.template_name, {'form': form, 'guardado': guardado})


class VistaCrearReporteComentario(LoginRequiredMixin, View):
    template_name = 'reportes/reportes_crear.html'

    def get(self, request, comment_pk):
        comentario = get_object_or_404(Comentario, pk=comment_pk)
        if ReporteComentario.objects.filter(comentario=comentario, reportado_por=request.user).exists():
            messages.warning(request, 'Ya has reportado este comentario.')
            return redirect('juegos:juego_detalle', pk=comentario.juego.pk)
        return render(request, self.template_name, {'form': FormularioReporteComentario(), 'comentario': comentario})

    def post(self, request, comment_pk):
        comentario = get_object_or_404(Comentario, pk=comment_pk)
        # Prevenir reportes duplicados del mismo usuario sobre el mismo comentario.
        if ReporteComentario.objects.filter(comentario=comentario, reportado_por=request.user).exists():
            messages.warning(request, 'Ya has reportado este comentario.')
            return redirect('juegos:juego_detalle', pk=comentario.juego.pk)

        form = FormularioReporteComentario(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.comentario = comentario
            reporte.reportado_por = request.user
            reporte.save()
            try:
                send_mail(
                    subject=f'[SaveVault] Nuevo reporte de comentario en: {comentario.juego.titulo}',
                    message=(
                        f'Se ha reportado un comentario.\n\n'
                        f'Juego: {comentario.juego.titulo} ({comentario.juego.plataforma})\n'
                        f'Comentario de: {comentario.usuario}\n'
                        f'Texto: {comentario.texto}\n'
                        f'Reportado por: {request.user}\n'
                        f'Motivo: {reporte.get_motivo_display()}\n'
                        f'Detalle: {reporte.detalle}\n\n'
                        f'Por favor, revísalo en el panel de administración.'
                    ),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@savevault.com'),
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Reporte enviado. Gracias por ayudar a mantener SaveVault limpio.')
            return redirect('juegos:juego_detalle', pk=comentario.juego.pk)

        return render(request, self.template_name, {'form': form, 'comentario': comentario})
