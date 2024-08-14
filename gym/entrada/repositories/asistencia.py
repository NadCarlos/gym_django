from typing import List, Optional

from administracion.models import Asistencia, PrestacionPaciente


class AsistenciaRepository:

    def get_all(self) -> List[Asistencia]:
        return Asistencia.objects.all()
    
    def get_all_by_id(self, id_prestacion_paciente) -> List[Asistencia]:
        return Asistencia.objects.filter(id_prestacion_paciente=id_prestacion_paciente)
    
    def filter_by_id(self) -> Optional[Asistencia]:
        return Asistencia.objects.filter(id=id).first()
    
    def get_by_id(self, id: int) -> Optional[Asistencia]:
        try:
            asistencia = Asistencia.objects.get(id=id)
        except:
            asistencia = None
        return asistencia
    
    def delete(self, asistencia: Asistencia):
        return asistencia.delete()
    
    def create(
        self,
        prestacionPaciente: PrestacionPaciente,
    ):
        return Asistencia.objects.create(
            id_prestacion_paciente=prestacionPaciente,
        )