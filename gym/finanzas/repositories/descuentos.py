from typing import List, Optional

from finanzas.models import Descuento, Concepto, OrdenPago


class DescuentoRepository:

    def filter_by_orden_id(self, orden_id) -> Optional[Descuento]:
        return Descuento.objects.filter(id_ordenpago=orden_id).filter(activo = True)
    
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