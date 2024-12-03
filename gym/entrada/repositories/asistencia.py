from typing import List, Optional

from administracion.models import Asistencia, PrestacionPaciente, Agenda


class AsistenciaRepository:

    def get_all(self) -> List[Asistencia]:
        return Asistencia.objects.all().order_by('fecha')
    
    def get_all_by_id(self, id_prestacion_paciente) -> List[Asistencia]:
        return Asistencia.objects.filter(id_prestacion_paciente=id_prestacion_paciente)
    
    def filter_by_id(self) -> Optional[Asistencia]:
        return Asistencia.objects.filter(id=id).first()

    def filter_by_dates(self, start_date, end_date) -> Optional[Asistencia]:
        return Asistencia.objects.filter(fecha__gte=start_date, fecha__lt=end_date)
    
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
        agenda: Optional[Agenda] = None,
    ):
        return Asistencia.objects.create(
            id_prestacion_paciente=prestacionPaciente,
            id_agenda=agenda,
        )