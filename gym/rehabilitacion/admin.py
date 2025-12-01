from django.contrib import admin

from rehabilitacion.models import(
    EstadoCertificado,
    Derivador,
    PacienteRehabilitacion,
    TipoDiscapacidad,
    DiagnosticoEtiologico,
    Alta,
)


@admin.register(EstadoCertificado)
class EstadoCertificadoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Derivador)
class DerivadorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(PacienteRehabilitacion)
class PacienteRehabilitacionAdmin(admin.ModelAdmin):
    list_display = (
        'id_paciente_area',
    )


@admin.register(TipoDiscapacidad)
class TipoDiscapacidadAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(DiagnosticoEtiologico)
class DiagnosticoEtiologicoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Alta)
class AltaAdmin(admin.ModelAdmin):
    list_display = (
        'id_paciente_rehabilitacion',
    )