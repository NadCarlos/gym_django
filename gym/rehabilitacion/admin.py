from django.contrib import admin

from rehabilitacion.models import(
    EstadoCertificado,
    Derivador,
    PacienteRehabilitacion,
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