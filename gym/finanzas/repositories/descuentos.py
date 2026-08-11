from typing import List, Optional

from django.db.models import Sum

from finanzas.models import Descuento, Concepto, OrdenPago


class DescuentoRepository:

    def total_activo(self):
        return Descuento.objects.filter(
            activo=True,
            id_ordenpago__activo=True,
        ).aggregate(total=Sum("importe"))["total"] or 0

    def total_activo_por_beneficiario(self, beneficiario_id):
        return Descuento.objects.filter(
            activo=True,
            id_ordenpago__activo=True,
            id_ordenpago__id_beneficiario=beneficiario_id,
        ).aggregate(total=Sum("importe"))["total"] or 0

    def filter_by_orden_id(self, orden_id) -> Optional[Descuento]:
        return Descuento.objects.filter(
            id_ordenpago=orden_id,
            activo=True,
        ).select_related("id_concepto", "id_ordenpago")
    
    def filter_by_id(self, id) -> Optional[Descuento]:
        return Descuento.objects.filter(id=id).first()
    
    def create(
            self,
            observaciones: str,
            importe: float,
            id_ordenpago: OrdenPago,
            id_concepto: Concepto,
        ):
            return Descuento.objects.create(
                observaciones=observaciones,
                importe=importe,
                id_ordenpago=id_ordenpago,
                id_concepto=id_concepto,
            )
    
    def update_activo(
        self, 
        descuento: Descuento,
        activo: bool,
    ) -> Descuento:

        descuento.activo = activo

        descuento.save()