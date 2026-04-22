from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.generic import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import LoginView as BaseLoginView

from .models import Usuario
from .forms import FormularioRegistro, FormularioEditarPerfil, FormularioLogin


class VistaRegistro(View):
    template_name = 'usuarios/usuarios_registro.html'

    def get(self, request):
        # Si el usuario ya está autenticado, no mostrar el formulario de registro.
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name, {'form': FormularioRegistro()})

    def post(self, request):
        # Procesar el registro de un nuevo usuario y hacer login inmediato.
        form = FormularioRegistro(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido, {usuario.username}!')
            return redirect('home')
        return render(request, self.template_name, {'form': form})


class VistaLogin(BaseLoginView):
    template_name = 'usuarios/usuarios_acceder.html'
    authentication_form = FormularioLogin
    redirect_authenticated_user = True


class VistaPerfil(View):
    template_name = 'usuarios/usuarios_perfil.html'

    def get(self, request, username):
        # Mostrar el perfil de usuario y sus guardados activos con paginación.
        usuario = get_object_or_404(Usuario, username=username)
        qs = usuario.guardados_subidos.filter(activo=True).select_related('juego__plataforma').order_by('-subido_en')
        paginator = Paginator(qs, 10)
        page = request.GET.get('page', 1)
        guardados = paginator.get_page(page)
        return render(request, self.template_name, {'usuario_perfil': usuario, 'guardados': guardados})


class VistaEditarPerfil(LoginRequiredMixin, View):
    template_name = 'usuarios/usuarios_editar.html'

    def get(self, request):
        return render(request, self.template_name, {'form': FormularioEditarPerfil(instance=request.user)})

    def post(self, request):
        # Guardar los cambios del perfil, incluyendo posible avatar nuevo.
        form = FormularioEditarPerfil(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:usuario_perfil', username=request.user.username)
        # Refrescar el usuario desde la base de datos para mostrar el avatar actual.
        usuario_actual = request.user.__class__.objects.get(pk=request.user.pk)
        return render(request, self.template_name, {'form': form, 'usuario_actual': usuario_actual})


class VistaEliminarCuenta(LoginRequiredMixin, View):
    template_name = 'usuarios/usuarios_eliminar.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Eliminar cuenta y cerrar sesión.
        usuario = request.user
        logout(request)
        usuario.delete()
        messages.success(request, 'Tu cuenta ha sido eliminada.')
        return redirect('home')


class VistaBaneado(LoginRequiredMixin, View):
    template_name = 'usuarios/usuarios_baneado.html'

    def get(self, request):
        # Mostrar el tiempo restante del baneo para usuarios baneados.
        if not request.user.is_baneado:
            return redirect('home')

        tiempo = request.user.tiempo_restante_baneo
        if tiempo:
            dias = tiempo.days
            horas = tiempo.seconds // 3600
            minutos = (tiempo.seconds % 3600) // 60
            segundos = tiempo.seconds % 60
            tiempo_restante = []
            if dias:
                tiempo_restante.append(f'{dias} día' + ('s' if dias != 1 else ''))
            if horas:
                tiempo_restante.append(f'{horas} hora' + ('s' if horas != 1 else ''))
            if minutos:
                tiempo_restante.append(f'{minutos} minuto' + ('s' if minutos != 1 else ''))
            if segundos or not tiempo_restante:
                tiempo_restante.append(f'{segundos} segundo' + ('s' if segundos != 1 else ''))
            tiempo_restante = ', '.join(tiempo_restante)
        else:
            tiempo_restante = 'menos de un segundo'

        return render(request, self.template_name, {'tiempo_restante': tiempo_restante})

