from django.urls import path
from . import views
from . import api

app_name = 'juegos'
# Rutas para la lista, detalle, creación de juegos y endpoints AJAX/API.

urlpatterns = [
    path('', views.ListaJuegos.as_view(), name='juego_lista'),
    path('crear/', views.VistaCrearJuego.as_view(), name='juego_crear'),
    path('<int:pk>/', views.VistaDetalleJuego.as_view(), name='juego_detalle'),
    path('plataforma/<slug:slug>/', views.VistaDetallePlataforma.as_view(), name='plataforma_detalle'),
    path('comentario/<int:pk>/eliminar/', views.EliminarComentario.as_view(), name='comentario_eliminar'),
    path('api/juegos/', api.api_games_list, name='api_juegos'),
    path('api/juego/', api.api_game_detail, name='api_juego'),
    path('api/buscar/', api.api_buscar_local, name='api_buscar'),
]
