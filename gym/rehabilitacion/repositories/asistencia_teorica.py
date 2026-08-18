from typing import List, Optional

from django.db.models import Count, F, Sum

from rehabilitacion.models import AsistenciaRehabTeorica, AgendaRehab


class AsistenciaRehabTeoricaRepository:

    def get_all(self) -> List[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.all().order_by('fecha')
    
    def filter_by_id(self) -> Optional[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.filter(id=id).first()

    def filter_by_dates(self, start_date, end_date) -> Optional[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.filter(fecha__gte=start_date, fecha__lt=end_date)
    
    def filter_by_date(self,id_paciente, fecha) -> Optional[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.filter(id_agenda_rehab__id_paciente_area__id_paciente__id=id_paciente).filter(fecha=fecha)

    def filter_by_agenda_date(self, id_agenda_rehab, fecha) -> Optional[AsistenciaRehabTeorica]:
        return AsistenciaRehabTeorica.objects.filter(
            id_agenda_rehab_id=id_agenda_rehab,
            fecha=fecha,
        )

    def horas_por_profesional(self, fecha_desde, fecha_hasta, id_area, ordering):
        return (
            AsistenciaRehabTeorica.objects
            .filter(
                fecha__gte=fecha_desde,
                fecha__lte=fecha_hasta,
                id_agenda_rehab__isnull=False,
                id_agenda_rehab__id_paciente_area__id_area_id=id_area,
                id_agenda_rehab__id_profesional_area__id_area_id=id_area,
            )
            .values(
                profesional_id=F('id_agenda_rehab__id_profesional_area__id_profesional__id'),
                apellido=F('id_agenda_rehab__id_profesional_area__id_profesional__apellido'),
                nombre=F('id_agenda_rehab__id_profesional_area__id_profesional__nombre'),
                matricula=F('id_agenda_rehab__id_profesional_area__id_profesional__matricula'),
            )
            .annotate(
                total_horas=Sum('id_agenda_rehab__tiempo'),
                total_agendas=Count('id'),
            )
            .order_by(ordering, 'apellido', 'nombre')
        )

    def total_horas_por_profesional_area(self, id_profesional_area, fecha_desde, fecha_hasta, id_area):
        return (
            AsistenciaRehabTeorica.objects
            .filter(
                fecha__gte=fecha_desde,
                fecha__lt=fecha_hasta,
                id_agenda_rehab__id_profesional_area_id=id_profesional_area,
                id_agenda_rehab__id_paciente_area__id_area_id=id_area,
                id_agenda_rehab__id_profesional_area__id_area_id=id_area,
            )
            .aggregate(total_horas=Sum('id_agenda_rehab__tiempo'))
            .get('total_horas') or 0
        )
    
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
        fecha = None,
    ):
        asistencia = AsistenciaRehabTeorica.objects.create(
            id_agenda_rehab=id_agenda_rehab,
        )
        if fecha:
            asistencia.fecha = fecha
            asistencia.save(update_fields=["fecha"])
        return asistencia
