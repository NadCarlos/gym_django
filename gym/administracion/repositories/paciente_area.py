from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import PacienteArea, Area, Paciente


class PacienteAreaRepository:

    def get_all(self) -> List[PacienteArea]:
        return PacienteArea.objects.all()
    
    def filter_by_id(self, id) -> Optional[PacienteArea]:
        return PacienteArea.objects.filter(id=id).first()
    
    def filter_by_id_area_and_paciente(self, id_area, id_paciente) -> Optional[PacienteArea]:
        return PacienteArea.objects.filter(id_paciente=id_paciente).filter(id_area=id_area).first()

    def create_default(
        self,
        id_paciente: Paciente,
        id_usuario: User
    ):
        return PacienteArea.objects.create(
            id_paciente=id_paciente,
            id_usuario=id_usuario,
        )
    
    def create(
        self,
        id_paciente: Paciente,
        id_area: Area,
        id_usuario: User
    ):
        return PacienteArea.objects.create(
            id_paciente=id_paciente,
            id_area=id_area,
            id_usuario=id_usuario,
        )
    
    def delete_by_activo(self, paciente_area: PacienteArea):
        paciente_area.activo=False
        paciente_area.save()