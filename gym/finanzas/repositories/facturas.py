from typing import List, Optional

from finanzas.models import Factura, Beneficiario


class FacturaRepository:

    def get_all(self) -> List[Factura]:
        return Factura.objects.all()
    
    def filter_by_id(self, id) -> Optional[Factura]:
        return Factura.objects.filter(id=id).first()
    
    def filter_by_activo(self) -> List[Factura]:
        return Factura.objects.filter(
            activo=True
        ).order_by('nombre')
    
    def filter_by_date(self, year, month) -> Optional[Factura]:
        return Factura.objects.filter(fecha__year=year, fecha__month=month)
    
    def filter_by_dates(self, start_date, end_date) -> Optional[Factura]:
        return Factura.objects.filter(fecha__gte=start_date, fecha__lt=end_date)
    
    def filter_by_numero_fact(self, fact_numero: str, pto_vta: str) -> List[Factura]:
        return Factura.objects.filter(pto_vta=pto_vta).filter(numero=fact_numero).first()
    
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