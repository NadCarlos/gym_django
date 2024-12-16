from django.contrib import admin

from finanzas.models import (
    Beneficiario,
    Factura,
)


@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
    )
