from .models import Plataforma


def plataformas_menu(request):
    return {'all_platforms': Plataforma.objects.all()}
