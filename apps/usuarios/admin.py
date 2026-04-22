from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Extiende el admin estándar de Django para mostrar campos adicionales de moderación.
    list_display = [
        'username', 'email', 'is_staff', 'is_baneado', 'baneo_hasta',
        'reportes_confirmados', 'date_joined', 'total_contributions'
    ]
    readonly_fields = ['baneo_hasta', 'reportes_confirmados']
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil', {'fields': ('bio', 'avatar')}),
        ('Moderación', {'fields': ('reportes_confirmados', 'baneo_hasta')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Perfil', {'fields': ('email', 'bio', 'avatar')}),
    )

    @admin.display(boolean=True, description='Baneado')
    def is_baneado(self, obj):
        return obj.is_baneado
