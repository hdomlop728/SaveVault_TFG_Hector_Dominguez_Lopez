from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path, reverse

from .models import ReporteComentario, ReporteGuardado

# Solo el personal de staff puede ver y gestionar los reportes, no hay que complicar permisos por objeto.
class StaffAdminMixin:
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

# Eliminar permisos de edición y borrado por separado, se gestionan con acciones y botones personalizados en la interfaz.
class ReporteAdminBase(StaffAdminMixin, admin.ModelAdmin):
    """
    Clase base para ReporteComentarioAdmin y ReporteGuardadoAdmin, con configuración común.
    Define permisos para que solo el staff pueda acceder, y elimina permisos de edición/borrado estándar.
    """
    list_display_links = ['ver_reporte']
    list_filter = ['estado', 'motivo', 'creado_en']
    readonly_fields = ['creado_en', 'reportado_por', 'resuelto_en', 'resuelto_por']
    ordering = ['-creado_en']

    def get_actions(self, request):
        return super().get_actions(request)

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        queryset.delete()

    @admin.display(description='#')
    def ver_reporte(self, obj):
        return f'#{obj.pk}'

    @admin.display(description='Motivo')
    def motivo_badge(self, obj):
        # Mapea cada motivo de reporte a un color visual en el admin.
        colores = {
            'broken': '#f0a500',
            'wrong_game': '#6c757d',
            'wrong_region': '#17a2b8',
            'malware': '#dc3545',
            'otro': '#6f42c1',
            'spam': '#dc3545',
            'abuso': '#dc3545',
            'irrelevante': '#6c757d',
            'informacion_falsa': '#6c757d',
        }
        color = colores.get(obj.motivo, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px; '
            'border-radius:4px;font-size:.75rem;font-weight:600">{}</span>',
            color, obj.get_motivo_display()
        )

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        # Muestra la etiqueta de estado con un color según la situación del reporte.
        colores = {
            'pending': '#f0a500',
            'reviewing': '#17a2b8',
            'resolved': '#28a745',
            'dismissed': '#6c757d',
        }
        color = colores.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px; '
            'border-radius:4px;font-size:.75rem">{}</span>',
            color, obj.get_estado_display()
        )

    @admin.display(description='Detalle')
    def detalle_texto(self, obj):
        # Mostrar texto de detalle truncado para no romper la tabla del admin.
        if not obj.detalle:
            return format_html('<span style="color:#888;font-size:.8em">—</span>')
        return format_html(
            '<span style="font-size:.82em;max-width:200px;display:inline-block;'
            'white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="{}">{}</span>',
            obj.detalle, obj.detalle
        )

    @admin.action(description='✔ Sin problema — descartar')
    def accion_sin_problema(self, request, queryset):
        n = queryset.update(
            estado='dismissed',
            resuelto_en=timezone.now(),
            resuelto_por=request.user,
        )
        self.message_user(request, f'{n} reporte(s) descartado(s).')


@admin.register(ReporteGuardado)
class ReporteGuardadoAdmin(ReporteAdminBase):
    list_display = [
        'ver_reporte', 'enlace_juego', 'info_guardado', 'reportado_por',
        'motivo_badge', 'detalle_texto', 'num_reportes', 'estado_badge',
        'creado_en', 'acciones'
    ]
    search_fields = [
        'archivo_guardado__juego__titulo', 'reportado_por__username',
        'archivo_guardado__subido_por__username'
    ]
    readonly_fields = ['creado_en', 'reportado_por', 'archivo_guardado',
                       'resuelto_en', 'resuelto_por', 'vista_previa_guardado']
    actions = ['accion_sin_problema', 'accion_eliminar_guardado']

    fieldsets = [
        ('Detalles del reporte', {
            'fields': ['vista_previa_guardado', 'reportado_por', 'motivo', 'detalle', 'estado', 'creado_en']
        }),
        ('Resolución', {
            'fields': ['resuelto_por', 'resuelto_en'],
            'classes': ['collapse'],
        }),
    ]

    def enlace_juego(self, obj):
        if not obj.archivo_guardado:
            return '—'
        juego = obj.archivo_guardado.juego
        url = reverse('admin:juegos_juego_change', args=[juego.pk])
        return format_html('<a href="{}">{}</a>', url, juego.titulo)

    def info_guardado(self, obj):
        if not obj.archivo_guardado:
            return format_html('<span style="color:#888">Guardado eliminado</span>')
        sf = obj.archivo_guardado
        url_admin = reverse('admin:guardados_archivoguardado_change', args=[sf.pk])
        return format_html(
            '<a href="{}" style="font-size:.8em">{} · por <strong>{}</strong></a>',
            url_admin, sf.region, sf.subido_por.username
        )

    def num_reportes(self, obj):
        if not obj.archivo_guardado:
            return '—'
        n = obj.archivo_guardado.reportes_guardado.count()
        color = '#dc3545' if n >= 3 else '#f0a500' if n == 2 else '#6c757d'
        return format_html('<strong style="color:{}">{}</strong>', color, n)

    def vista_previa_guardado(self, obj):
        if not obj.archivo_guardado:
            return 'El archivo de guardado ha sido eliminado.'
        sf = obj.archivo_guardado
        return format_html(
            '<table style="font-size:.9em">'
            '<tr><th style="text-align:left;padding-right:16px">Juego</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Plataforma</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Región</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Subido por</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Descargas</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Reportes totales</th><td>{}</td></tr>'
            '</table>',
            sf.juego.titulo, sf.juego.plataforma, sf.region,
            sf.subido_por.username, sf.num_descargas, sf.reportes_guardado.count()
        )

    def acciones(self, obj):
        if obj.estado in ('resolved', 'dismissed'):
            return format_html('<span style="color:#6c757d;font-size:.8em">Cerrado</span>')
        ok_url = reverse('admin:reportes_reporteguardado_sinproblema', args=[obj.pk])
        del_url = reverse('admin:reportes_reporteguardado_eliminar', args=[obj.pk])
        return format_html(
            '<a href="{}" style="margin-right:10px;color:#28a745;font-weight:600;font-size:.85em"'
            ' title="Sin problema — conservar guardado">✔ Sin problema</a>'
            '<a href="{}" style="color:#dc3545;font-weight:600;font-size:.85em"'
            ' title="Eliminar guardado">🗑 Eliminar guardado</a>',
            ok_url, del_url
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:pk>/sinproblema/', self.admin_site.admin_view(self.vista_sin_problema), name='reportes_reporteguardado_sinproblema'),
            path('<int:pk>/eliminar/', self.admin_site.admin_view(self.vista_eliminar), name='reportes_reporteguardado_eliminar'),
        ]
        return custom + urls

    def _get(self, pk):
        return ReporteGuardado.objects.select_related('archivo_guardado__juego', 'archivo_guardado__subido_por').get(pk=pk)

    def _volver(self):
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('admin:reportes_reporteguardado_changelist'))

    def vista_sin_problema(self, request, pk):
        r = self._get(pk)
        r.estado = 'dismissed'
        r.resuelto_en = timezone.now()
        r.resuelto_por = request.user
        r.save()
        titulo = r.archivo_guardado.juego.titulo if r.archivo_guardado else '(desconocido)'
        self.message_user(request, f'Reporte descartado — guardado de "{titulo}" conservado.')
        return self._volver()

    def vista_eliminar(self, request, pk):
        import os
        r = self._get(pk)
        sf = r.archivo_guardado
        if sf:
            titulo = sf.juego.titulo
            ReporteGuardado.objects.filter(archivo_guardado=sf).update(
                estado='resolved',
                resuelto_en=timezone.now(),
                resuelto_por=request.user,
            )
            autor = sf.subido_por
            if autor:
                autor.marcar_reporte_confirmado()
            if sf.archivo and sf.archivo.path and os.path.isfile(sf.archivo.path):
                os.remove(sf.archivo.path)
            sf.delete()
            self.message_user(request, f'Guardado de "{titulo}" eliminado permanentemente. Reportes resueltos.')
        else:
            self.message_user(request, 'El guardado ya había sido eliminado.')
        return self._volver()

    @admin.action(description='🗑 Eliminar guardados reportados y resolver reportes')
    def accion_eliminar_guardado(self, request, queryset):
        import os
        from collections import defaultdict
        
        # Contar reportes por usuario propietario del guardado
        reportes_por_usuario = defaultdict(int)
        guardados_a_eliminar = {}
        
        for reporte in queryset.select_related('archivo_guardado__subido_por').filter(archivo_guardado__isnull=False):
            sf = reporte.archivo_guardado
            guardados_a_eliminar[sf.pk] = sf
            if sf.subido_por:
                reportes_por_usuario[sf.subido_por] += 1

        # Actualizar estado de todos los reportes
        ReporteGuardado.objects.filter(
            archivo_guardado__in=guardados_a_eliminar.keys()
        ).update(
            estado='resolved',
            resuelto_en=timezone.now(),
            resuelto_por=request.user,
        )

        # Sumar reportes confirmados a cada usuario propietario
        for usuario, num_reportes in reportes_por_usuario.items():
            usuario.marcar_reportes_confirmados(cantidad=num_reportes)

        # Eliminar los guardados y sus archivos
        eliminados = 0
        for sf in guardados_a_eliminar.values():
            if sf.archivo and sf.archivo.path and os.path.isfile(sf.archivo.path):
                os.remove(sf.archivo.path)
            sf.delete()
            eliminados += 1

        self.message_user(request, f'{eliminados} guardado(s) eliminado(s) y reportes resueltos.')


@admin.register(ReporteComentario)
class ReporteComentarioAdmin(ReporteAdminBase):
    list_display = [
        'ver_reporte', 'enlace_juego', 'info_comentario', 'reportado_por',
        'motivo_badge', 'detalle_texto', 'estado_badge', 'creado_en', 'acciones'
    ]
    search_fields = [
        'comentario__juego__titulo', 'comentario__usuario__username', 'reportado_por__username'
    ]
    readonly_fields = ['creado_en', 'reportado_por', 'comentario',
                       'resuelto_en', 'resuelto_por', 'vista_previa_comentario']
    actions = ['accion_sin_problema', 'accion_eliminar_comentario']

    fieldsets = [
        ('Detalles del reporte', {
            'fields': ['vista_previa_comentario', 'reportado_por', 'motivo', 'detalle', 'estado', 'creado_en']
        }),
        ('Resolución', {
            'fields': ['resuelto_por', 'resuelto_en'],
            'classes': ['collapse'],
        }),
    ]

    def enlace_juego(self, obj):
        if not obj.comentario:
            return '—'
        juego = obj.comentario.juego
        url = reverse('admin:juegos_juego_change', args=[juego.pk])
        return format_html('<a href="{}">{}</a>', url, juego.titulo)

    def info_comentario(self, obj):
        if not obj.comentario:
            return format_html('<span style="color:#888">Comentario eliminado</span>')
        c = obj.comentario
        url_admin = reverse('admin:juegos_comentario_change', args=[c.pk])
        return format_html(
            '<a href="{}" style="font-size:.8em">Comentario de <strong>{}</strong></a>',
            url_admin, c.usuario.username
        )

    def num_reportes(self, obj):
        if not obj.comentario:
            return '—'
        n = obj.comentario.reportes_comentario.count()
        color = '#dc3545' if n >= 3 else '#f0a500' if n == 2 else '#6c757d'
        return format_html('<strong style="color:{}">{}</strong>', color, n)

    def vista_previa_comentario(self, obj):
        if not obj.comentario:
            return 'El comentario ha sido eliminado.'
        c = obj.comentario
        return format_html(
            '<table style="font-size:.9em">'
            '<tr><th style="text-align:left;padding-right:16px">Juego</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Comentario</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Publicado por</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Fecha</th><td>{}</td></tr>'
            '<tr><th style="text-align:left;padding-right:16px">Reportes totales</th><td>{}</td></tr>'
            '</table>',
            c.juego.titulo, c.texto[:100], c.usuario.username,
            c.creado_en.strftime('%d/%m/%Y'), c.reportes_comentario.count()
        )

    def acciones(self, obj):
        if obj.estado in ('resolved', 'dismissed'):
            return format_html('<span style="color:#6c757d;font-size:.8em">Cerrado</span>')
        # Construir enlaces de acción rápida para descartar o eliminar reportes.
        ok_url = reverse('admin:reportes_reportecomentario_sinproblema', args=[obj.pk])
        delete_url = reverse('admin:reportes_reportecomentario_eliminar', args=[obj.pk])
        return format_html(
            '<a href="{}" style="margin-right:10px;color:#28a745;font-weight:600;font-size:.85em"'
            ' title="Sin problema — descartar">✔ Sin problema</a>'
            '<a href="{}" style="color:#dc3545;font-weight:600;font-size:.85em"'
            ' title="Eliminar comentario">🗑 Eliminar comentario</a>',
            ok_url, delete_url
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:pk>/sinproblema/', self.admin_site.admin_view(self.vista_sin_problema), name='reportes_reportecomentario_sinproblema'),
            path('<int:pk>/eliminar/', self.admin_site.admin_view(self.vista_eliminar), name='reportes_reportecomentario_eliminar'),
        ]
        return custom + urls

    def _get(self, pk):
        return ReporteComentario.objects.select_related('comentario__juego', 'comentario__usuario').get(pk=pk)

    def _volver(self):
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('admin:reportes_reportecomentario_changelist'))

    def vista_sin_problema(self, request, pk):
        r = self._get(pk)
        r.estado = 'dismissed'
        r.resuelto_en = timezone.now()
        r.resuelto_por = request.user
        r.save()
        self.message_user(request, 'Reporte de comentario descartado.')
        return self._volver()

    def vista_eliminar(self, request, pk):
        r = self._get(pk)
        c = r.comentario
        if c:
            titulo = c.juego.titulo
            ReporteComentario.objects.filter(comentario=c).update(
                estado='resolved',
                resuelto_en=timezone.now(),
                resuelto_por=request.user,
            )
            autor = c.usuario
            if autor:
                autor.marcar_reporte_confirmado()
            c.delete()
            self.message_user(request, f'Comentario de "{titulo}" eliminado permanentemente. Reportes resueltos.')
        else:
            self.message_user(request, 'El comentario ya había sido eliminado.')
        return self._volver()

    @admin.action(description='🗑 Eliminar comentarios reportados y resolver reportes')
    def accion_eliminar_comentario(self, request, queryset):
        from collections import defaultdict
        
        # Contar reportes por usuario propietario del comentario
        reportes_por_usuario = defaultdict(int)
        comentarios_a_eliminar = {}
        
        for reporte in queryset.select_related('comentario__usuario').filter(comentario__isnull=False):
            c = reporte.comentario
            comentarios_a_eliminar[c.pk] = c
            if c.usuario:
                reportes_por_usuario[c.usuario] += 1

        # Actualizar estado de todos los reportes
        ReporteComentario.objects.filter(
            comentario__in=comentarios_a_eliminar.keys()
        ).update(
            estado='resolved',
            resuelto_en=timezone.now(),
            resuelto_por=request.user,
        )

        # Sumar reportes confirmados a cada usuario propietario
        for usuario, num_reportes in reportes_por_usuario.items():
            usuario.marcar_reportes_confirmados(cantidad=num_reportes)

        # Eliminar los comentarios
        eliminados = 0
        for c in comentarios_a_eliminar.values():
            c.delete()
            eliminados += 1

        self.message_user(request, f'{eliminados} comentario(s) eliminado(s) y reportes resueltos.')
