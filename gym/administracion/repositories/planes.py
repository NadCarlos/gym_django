from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Plan


class PlanRepository:

    def get_all(self) -> List[Plan]:
        return Plan.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Plan]:
        return Plan.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Plan]:
        return Plan.objects.filter(id=id)
    
    def filter_by_activo(self) -> List[Plan]:
        return Plan.objects.filter(activo=True).order_by('nombre')
    
    def delete_by_activo(self, plan: Plan):
        plan.activo=False
        plan.save()
    
    def create(
        self,
        nombre: str,
        descripcion: str,
        valor: float,
        id_usuario: User,
    ):
        return Plan.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            valor=valor,
            id_usuario=id_usuario,
        )
    
    def update(
        self, 
        plan: Plan,
        nombre: str,
        descripcion: str,
        valor: float,
    ) -> Plan:
        plan.nombre = nombre
        plan.descripcion = descripcion
        plan.valor = valor

        plan.save()