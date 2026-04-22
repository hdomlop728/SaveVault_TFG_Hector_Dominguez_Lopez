from django.contrib import admin
from .models import CapturaPantalla, Plataforma, Genero, Juego, Comentario


class StaffAdminMixin:
    # Restringe el acceso a las vistas del admin solo a usuarios staff activos.
    # Esto protege modelos sensibles relacionados con juegos y reportes.
    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


@admin.register(Plataforma)
class PlataformaAdmin(StaffAdminMixin, admin.ModelAdmin):
    list_display = ['slug', 'nombre']


@admin.register(Genero)
class GeneroAdmin(StaffAdminMixin, admin.ModelAdmin):
    list_display = ['nombre']


@admin.register(Juego)
class JuegoAdmin(StaffAdminMixin, admin.ModelAdmin):
    list_display   = ['titulo', 'plataforma', 'desarrollador', 'genero', 'visitas', 'creado_en']
    list_filter    = ['plataforma', 'genero']
    search_fields  = ['titulo', 'desarrollador']
    readonly_fields = ['visitas', 'creado_en', 'portada_url']


@admin.register(Comentario)
class ComentarioAdmin(StaffAdminMixin, admin.ModelAdmin):
    list_display = ['usuario', 'juego', 'texto_corto', 'creado_en']
    list_filter  = ['creado_en']

    @admin.display(description='Comentario')
    def texto_corto(self, obj):
        from django.utils.html import format_html
        if len(obj.texto) > 80:
            return format_html('<span title="{}">{}</span>', obj.texto, obj.texto[:80] + '…')
        return obj.texto


@admin.register(CapturaPantalla)
class CapturaPantallaAdmin(StaffAdminMixin, admin.ModelAdmin):
    list_display  = ['juego', 'orden', 'url', 'añadido']
    list_filter   = ['juego__plataforma']
    raw_id_fields = ['juego']
