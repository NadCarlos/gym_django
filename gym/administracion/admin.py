from django.contrib import admin

from administracion.models import (
    Pais,
    Provincia,
    Localidad,
    ObraSocial,
    EstadoCivil,
    Sexo,
    Prestacion,
    Paciente,
    PrestacionPaciente,
    Asistencia,
)


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(EstadoCivil)
class EstadoCivilAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Sexo)
class SexoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Prestacion)
class PrestacionAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(PrestacionPaciente)
class PrestacionPacienteAdmin(admin.ModelAdmin):
    list_display = (
        'fecha_inicio',
    )


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = (
        'fecha',
    )
