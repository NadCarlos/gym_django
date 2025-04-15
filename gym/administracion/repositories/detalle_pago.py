from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import DetallePago, Pago, Cuota


class DetallePagoRepository:

    def get_all(self) -> List[DetallePago]:
        return DetallePago.objects.all()
    
    def filter_by_cuota_id(self, id_cuota) -> Optional[DetallePago]:
        return DetallePago.objects.filter(id_cuota=id_cuota)
    
    def create(
        self,
        importe: float,
        id_pago: Pago,
        id_cuota: Cuota,
    ):
        return DetallePago.objects.create(
            importe=importe,
            id_pago=id_pago,
            id_cuota=id_cuota,
        )