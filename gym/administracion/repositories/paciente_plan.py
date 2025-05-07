from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import PacientePlan, Plan


class PacientePlanRepository:

    def get_all(self) -> List[PacientePlan]:
        return PacientePlan.objects.all()
    
    def get_by_id(self, id: int) -> Optional[PacientePlan]:
        return PacientePlan.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[PacientePlan]:
        return PacientePlan.objects.filter(id=id)
    
    def filter_by_activo(self) -> List[PacientePlan]:
        return PacientePlan.objects.filter(activo=True)
    
    def filter_by_paciente_activo(self, id_paciente) -> List[PacientePlan]:
        return PacientePlan.objects.filter(id_paciente=id_paciente).filter(activo=True).first()
    
    def paciente_plan_exist(self, id_paciente) -> List[PacientePlan]:
        return PacientePlan.objects.filter(id_paciente=id_paciente).filter(activo=True).exists()
    
    def filter_by_paciente(self, id) -> List[PacientePlan]:
        return PacientePlan.objects.filter(id_paciente=id).order_by('-activo')
    
    def delete_by_activo(self, paciente_plan: PacientePlan):
        paciente_plan.activo=False
        paciente_plan.save()
    
    def create(
        self,
        id_plan: Plan,
        fecha: str,
        id_paciente: float,
        id_usuario: User,
    ):
        return PacientePlan.objects.create(
            id_plan=id_plan,
            fecha=fecha,
            id_paciente=id_paciente,
            id_usuario=id_usuario,
        )
    
    def update(
        self, 
        paciente_plan: PacientePlan,
        fecha: str,
    ) -> PacientePlan:
        paciente_plan.fecha = fecha

        paciente_plan.save()