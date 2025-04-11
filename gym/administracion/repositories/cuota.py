from typing import List, Optional

from administracion.models import Cuota, PacientePlan


class CuotaRepository:

    def get_all(self) -> List[Cuota]:
        return Cuota.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Cuota]:
        return Cuota.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Cuota]:
        return Cuota.objects.filter(id=id)
    
    def filter_by_activo(self) -> List[Cuota]:
        return Cuota.objects.filter(activo=True).order_by('nombre')
    
    def delete_by_activo(self, cuota: Cuota):
        cuota.anulado=False
        cuota.save()
    
    def create(
        self,
        imputado: str,
        id_paciente_plan: PacientePlan,
        valor: float,
    ):
        return Cuota.objects.create(
            imputado=imputado,
            id_paciente_plan=id_paciente_plan,
            valor=valor,
        )
