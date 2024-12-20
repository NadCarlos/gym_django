from typing import List, Optional

from finanzas.models import Factura, Beneficiario


class FacturaRepository:

    def get_all(self) -> List[Factura]:
        return Factura.objects.all()
    
    def filter_by_id(self) -> Optional[Factura]:
        return Factura.objects.filter(id=id).first()
    
    def filter_by_activo(self) -> List[Factura]:
        return Factura.objects.filter(
            activo=True
        ).order_by('nombre')
    
    def get_by_id(self, id: int) -> Optional[Factura]:
        try:
            factura = Factura.objects.get(id=id)
        except:
            factura = None
        return factura
    
    def delete(self, factura: Factura):
        return factura.delete()
    
    def delete_by_activo(self, factura: Factura):
        factura.activo=False
        factura.save()
    
    def create(
        self,
        tipo: str,
        pto_vta: str,
        numero: str,
        fecha: str,
        importe: float,
        id_beneficiario: Beneficiario,
    ):
        return Factura.objects.create(
            tipo=tipo,
            pto_vta=pto_vta,
            numero=numero,
            fecha=fecha,
            importe=importe,
            id_beneficiario=id_beneficiario,
        )