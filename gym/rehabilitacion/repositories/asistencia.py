from typing import List, Optional
from django.db.models import OuterRef

from rehabilitacion.models import AsistenciaRehab, AgendaRehab


class AsistenciaRehabRepository:

    def get_all(self) -> List[AsistenciaRehab]:
        return AsistenciaRehab.objects.all().order_by('fecha')
    
    def filter_by_id(self) -> Optional[AsistenciaRehab]:
        return AsistenciaRehab.objects.filter(id=id).first()

    def filter_by_dates(self, start_date, end_date) -> Optional[AsistenciaRehab]:
        return AsistenciaRehab.objects.filter(fecha__gte=start_date, fecha__lt=end_date)
    
    def filter_by_date(self,id_paciente, fecha) -> Optional[AsistenciaRehab]:
        return AsistenciaRehab.objects.filter(id_agenda_rehab__id_paciente_area__id_paciente__id=id_paciente).filter(fecha=fecha)

    def asistencias_cargadas_list(self, fecha, id_dia):
        return AsistenciaRehab.objects.filter(fecha=fecha,id_agenda_rehab__id_dia_id=id_dia,id_agenda_rehab__activo=True,
            id_agenda_rehab__id_paciente_area__id_paciente_id=OuterRef("pk"),
        )
    
    def get_by_id(self, id: int) -> Optional[AsistenciaRehab]:
        try:
            asistencia = AsistenciaRehab.objects.get(id=id)
        except:
            asistencia = None
        return asistencia
    
    def delete(self, asistencia: AsistenciaRehab):
        return asistencia.delete()
    
    def create(
        self,
        fecha: str,
        hora: str,
        id_agenda_rehab: Optional[AgendaRehab] = None,
    ):
        return AsistenciaRehab.objects.create(
            id_agenda_rehab=id_agenda_rehab,
            fecha=fecha,
            hora=hora,
        )

    def create_manual(
            self,
            fecha: str,
            hora: str,
            id_agenda_rehab: Optional[AgendaRehab] = None,
        ):
            asistencia = AsistenciaRehab.objects.create(
                id_agenda_rehab=id_agenda_rehab,
            )
            asistencia.fecha = fecha
            asistencia.hora = hora
            asistencia.save(update_fields=["fecha", "hora"])
            return asistencia