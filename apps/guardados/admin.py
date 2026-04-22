from django.contrib import admin
from .models import ArchivoGuardado


class StaffAdminMixin:
    # El mixin asegura que solo usuarios staff pueden ver y modificar los registros.
    # Esto evita que usuarios normales accedan al listado de guardados desde el admin.
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


@admin.register(ArchivoGuardado)
class ArchivoGuardadoAdmin(StaffAdminMixin, admin.ModelAdmin):
    list_display   = ['juego', 'region', 'subido_por', 'subido_en', 'num_descargas', 'activo']
    list_filter    = ['region', 'activo', 'juego__plataforma']
    search_fields  = ['juego__titulo', 'subido_por__username']
    readonly_fields = ['num_descargas', 'subido_en']
    list_editable  = ['activo']
