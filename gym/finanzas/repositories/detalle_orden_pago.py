from typing import List, Optional

from finanzas.models import DetalleOrden, Factura, OrdenPago


class DetalleOrdenRepo:

    def get_all(self) -> List[DetalleOrden]:
        return DetalleOrden.objects.all()

    def filter_by_id(self, id) -> Optional[DetalleOrden]:
        return DetalleOrden.objects.filter(id=id).first()
    
    def filter_by_orden_id(self, orden_id) -> Optional[DetalleOrden]:
        return DetalleOrden.objects.filter(id_ordenpago=orden_id).filter(activo = True)
    
    def filter_by_orden_pago_and_factura_id(self, factura_id, orden_id) -> Optional[DetalleOrden]:
        return DetalleOrden.objects.filter(id_ordenpago=orden_id).filter(id_factura=factura_id).filter(activo = True).first()
    
    def filter_by_factura_id(self, factura_id) -> Optional[DetalleOrden]:
        return DetalleOrden.objects.filter(id_factura=factura_id).filter(activo = True).first()
    
    def filter_by_factura_exists(self, id_factura) -> Optional[DetalleOrden]:
        return DetalleOrden.objects.filter(id_factura=id_factura).filter(activo = True).exists()
    
    def get_all_factura_ids_with_pago(self):
        return DetalleOrden.objects.values_list('id_factura', flat=True).distinct()
    
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
    
    def update(
        self, 
        detalle_orden: DetalleOrden,
        importe: str,
        id_ordenpago: OrdenPago,
        id_factura: Factura,
    ) -> DetalleOrden:

        detalle_orden.importe = importe
        detalle_orden.id_ordenpago = id_ordenpago
        detalle_orden.id_factura=id_factura

        detalle_orden.save()

    def delete_by_activo(self, detalle_orden: DetalleOrden):
        detalle_orden.activo=False
        detalle_orden.save()

    def update_activo(
        self, 
        detalle_orden: DetalleOrden,
        activo: bool,
    ) -> DetalleOrden:

        detalle_orden.activo = activo

        detalle_orden.save()