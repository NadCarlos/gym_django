from typing import List, Optional

from finanzas.models import DetalleOrden, Factura, OrdenPago


class DetalleOrdenRepo:

    def filter_by_id(self, id) -> Optional[DetalleOrden]:
        return DetalleOrden.objects.filter(id=id).first()
    
    def create(
        self,
        importe: str,
        id_ordenpago: OrdenPago,
        id_factura: Factura,
    ):
        return DetalleOrden.objects.create(
            importe=importe,
            id_ordenpago=id_ordenpago,
            id_factura=id_factura,
        )