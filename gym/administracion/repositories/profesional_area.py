from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import ProfesionalArea, Profesional, Area


class ProfesionalAreaRepository:

    def get_all(self) -> List[ProfesionalArea]:
        return ProfesionalArea.objects.all()
    
    def filter_by_id(self, id) -> Optional[ProfesionalArea]:
        return ProfesionalArea.objects.filter(id=id).first()
    
    def filter_by_profesional_id(self, id_profesional, id_area) -> Optional[ProfesionalArea]:
        return ProfesionalArea.objects.filter(id_profesional=id_profesional).filter(id_area=id_area).first()

    def create_default(
        self,
        id_profesional: Profesional,
        id_usuario: User
    ):
        return ProfesionalArea.objects.create(
            id_profesional=id_profesional,
            id_usuario=id_usuario,
        )
    
    def create(
        self,
        id_profesional: Profesional,
        id_area: Area,
        id_usuario: User
    ):
        return ProfesionalArea.objects.create(
            id_profesional=id_profesional,
            id_area=id_area,
            id_usuario=id_usuario,
        )
    
    def delete_by_activo(self, profesional_area: ProfesionalArea):
        profesional_area.activo=False
        profesional_area.save()