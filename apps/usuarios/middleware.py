from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone


class BaneoMiddleware:
    """Redirige a usuarios baneados a una pantalla única mientras el baneo esté activo."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        if request.user.is_staff:
            return None
        if not getattr(request.user, 'baneo_hasta', None):
            return None
        if not request.user.is_baneado:
            return None

        ban_path = reverse('usuarios:usuario_baneado')
        logout_path = reverse('usuarios:usuario_salir')
        allowed_paths = {ban_path, logout_path}

        # Permitir siempre el acceso a la página de baneo y el logout.
        if request.path in allowed_paths:
            return None

        # También permitir recursos estáticos y de medios incluso para usuarios baneados.
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        if request.path.startswith(static_url) or request.path.startswith(media_url):
            return None

        return redirect('usuarios:usuario_baneado')
