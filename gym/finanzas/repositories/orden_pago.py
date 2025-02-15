from typing import List, Optional

from django.contrib.auth.models import User
from finanzas.models import OrdenPago, Beneficiario


class OrdenPagoRepository:

    def get_all(self) -> List[OrdenPago]:
        return OrdenPago.objects.all()

    def filter_by_id(self, id) -> Optional[OrdenPago]:
        return OrdenPago.objects.filter(id=id).first()
    
    def filter_by_activo(self) -> List[OrdenPago]:
        return OrdenPago.objects.filter(activo=True).order_by('id_beneficiario__nombre')
    
    def filter_by_dates(self, start_date, end_date) -> Optional[OrdenPago]:
        return OrdenPago.objects.filter(activo=True).filter(fecha__gte=start_date, fecha__lt=end_date)
    
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