from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Pago, TipoPago, Paciente


class PagoRepository:

    def get_all(self) -> List[Pago]:
        return Pago.objects.all()
    
    def filter_by_id(self, id) -> Optional[Pago]:
        return Pago.objects.filter(id=id).first()

    def create(
        self,
        fecha: str,
        total: float,
        id_tipo_pago: TipoPago,
        id_paciente: Paciente,
        id_usuario: User
    ):
        return Pago.objects.create(
            fecha=fecha,
            total=total,
            id_tipo_pago=id_tipo_pago,
            id_paciente=id_paciente,
            id_usuario=id_usuario,
        )
    
    def delete_by_activo(self, pago: Pago):
        pago.activo=False
        pago.save()