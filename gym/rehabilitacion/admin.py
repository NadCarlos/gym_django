from django.contrib import admin

from rehabilitacion.models import(
    EstadoCertificado,
    Derivador,
    PacienteRehabilitacion,
    Familia,
    Diagnostico,
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


@admin.register(Familia)
class FamiliaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Alta)
class AltaAdmin(admin.ModelAdmin):
    list_display = (
        'id_paciente_rehabilitacion',
    )