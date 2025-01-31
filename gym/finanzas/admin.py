from django.contrib import admin

from finanzas.models import (
    Beneficiario,
    Factura,
    OrdenPago,
    Descuento,
    Concepto,
    DetalleOrden,
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


@admin.register(OrdenPago)
class OrdenPagoAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
    )


@admin.register(Descuento)
class DescuentoAdmin(admin.ModelAdmin):
    list_display = (
        'importe',
    )


@admin.register(Concepto)
class ConceptoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )


@admin.register(DetalleOrden)
class DetalleOrdenAdmin(admin.ModelAdmin):
    list_display = (
        'importe',
    )