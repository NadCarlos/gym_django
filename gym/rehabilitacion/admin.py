from django.contrib import admin

from rehabilitacion.models import(
    EstadoCertificado,
    Derivador,
    PacienteRehabilitacion,
    TipoDiscapacidad,
    DiagnosticoEtiologico,
    Alta,
    DiagnosticoFuncional,
    AltaFuncional,
    AgendaRehab,
    AsistenciaRehab,
    AsistenciaRehabTeorica,
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


@admin.register(DiagnosticoFuncional)
class DiagnosticoFuncionalAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(AltaFuncional)
class AltaFuncionalAdmin(admin.ModelAdmin):
    list_display = (
        'id_alta',
    )


@admin.register(AgendaRehab)
class AgendaRehabAdmin(admin.ModelAdmin):
    list_display = (
        'id_paciente_area',
    )


@admin.register(AsistenciaRehab)
class AsistenciaRehabAdmin(admin.ModelAdmin):
    list_display = (
        'id_agenda_rehab',
    )


@admin.register(AsistenciaRehabTeorica)
class AsistenciaRehabTeoricaAdmin(admin.ModelAdmin):
    list_display = (
        'id_agenda_rehab',
    )