from typing import List, Optional

from rehabilitacion.models import Informe
from administracion.models import Paciente, Profesional


class InformeRepository:

    def get_all(self) -> List[Informe]:
        return Informe.objects.all()

    def get_by_id(self, id: int) -> Optional[Informe]:
        return Informe.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Informe]:
        return Informe.objects.filter(id=id).first()
    
    def filter_by_paciente_id(self, paciente_id) -> Optional[Informe]:
        return Informe.objects.filter(id_paciente=paciente_id)
    
    def create(
        self,
        fecha: str,
        id_profesional: Profesional,
        id_paciente: Paciente,
        observaciones: str,
        ):
        return Informe.objects.create(
            fecha=fecha,
            id_profesional=id_profesional,
            id_paciente=id_paciente,
            observaciones=observaciones,
        )