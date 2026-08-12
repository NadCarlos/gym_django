from typing import List, Optional

from django.contrib.auth.models import User
from finanzas.models import OrdenPago, Beneficiario


class OrdenPagoRepository:

    def get_all(self) -> List[OrdenPago]:
        return OrdenPago.objects.select_related("id_beneficiario")

    def filter_by_id(self, id) -> Optional[OrdenPago]:
        return self.get_all().filter(id=id).first()
    
    def filter_by_activo(self) -> List[OrdenPago]:
        return self.get_all().filter(activo=True).order_by("id_beneficiario__nombre")
    
    def filter_by_beneficiario(self, id_beneficiario) -> List[OrdenPago]:
        return self.get_all().filter(id_beneficiario=id_beneficiario, activo=True)
    
    def filter_by_dates(self, start_date, end_date) -> Optional[OrdenPago]:
        return self.get_all().filter(
            activo=True,
            fecha__gte=start_date,
            fecha__lt=end_date,
        )
    
    def delete_by_activo(self, orden: OrdenPago):
        orden.activo=False
        orden.save()
    
    def create(
        self,
        id_usuario: User,
        fecha: str,
        numero: str,
        id_beneficiario: Beneficiario,
        total: str,
    ):
        return OrdenPago.objects.create(
            id_usuario=id_usuario,
            fecha=fecha,
            numero=numero,
            id_beneficiario=id_beneficiario,
            total=total,
        )
    
    def update_total(
        self,
        orden_pago: OrdenPago,
        total: str,
    ) -> OrdenPago:
        
        orden_pago.total = total
        orden_pago.save()