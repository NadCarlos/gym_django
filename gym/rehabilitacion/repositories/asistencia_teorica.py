from typing import List, Optional

from rehabilitacion.models import AsistenciaRehabTeorica, AgendaRehab


class AsistenciaRehabRepository:

    def get_all(self) -> List[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.all().order_by('fecha')
    
    def filter_by_id(self) -> Optional[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.filter(id=id).first()

    def filter_by_dates(self, start_date, end_date) -> Optional[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.filter(fecha__gte=start_date, fecha__lt=end_date)
    
    def filter_by_date(self,id_paciente, fecha) -> Optional[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.filter(id_agenda_rehab__id_paciente_area__id_paciente__id=id_paciente).filter(fecha=fecha)
    
    def get_by_id(self, id: int) -> Optional[AsistenciaRehabTeorica]:
        try:
            asistencia = AsistenciaRehabTeorica.objects.get(id=id)
        except:
            asistencia = None
        return asistencia
    
    def delete(self, asistencia: AsistenciaRehabTeorica):
        return asistencia.delete()
    
    def create(
        self,
        id_agenda_rehab: Optional[AgendaRehab] = None,
    ):
        return AsistenciaRehabTeorica.objects.create(
            id_agenda_rehab=id_agenda_rehab,
        )