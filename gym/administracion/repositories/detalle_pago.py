from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import DetallePago, Pago, Cuota


class DetallePagoRepository:

    def _with_display_relations(self):
        return DetallePago.objects.select_related(
            "id_cuota",
            "id_pago__id_tipo_pago",
        )

    def get_all(self) -> List[DetallePago]:
        return self._with_display_relations()
    
    def filter_by_cuota_id(self, id_cuota) -> Optional[DetallePago]:
        return DetallePago.objects.filter(id_cuota=id_cuota)
    
    def filter_by_pago_id(self, id_pago) -> Optional[DetallePago]:
        return DetallePago.objects.filter(id_pago=id_pago).first()
    
    def filter_by_paciente_id(self, id_paciente) -> Optional[DetallePago]:
        return self._with_display_relations().filter(
            id_cuota__id_paciente_plan__id_paciente__id=id_paciente,
            activo=True,
        )
    
    def filter_by_cuota_id_exists(self, id_cuota) -> Optional[DetallePago]:
        return DetallePago.objects.filter(id_cuota=id_cuota).exists()
    
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
    
    def delete_by_activo(self, detalle_pago: DetallePago):
        detalle_pago.activo=False
        detalle_pago.save()