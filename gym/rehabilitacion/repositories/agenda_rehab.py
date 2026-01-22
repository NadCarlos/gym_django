from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Dia, Tratamiento, PacienteArea, ProfesionalArea
from rehabilitacion.models import AgendaRehab


class AgendaRehabRepository:

    def get_all(self) -> List[AgendaRehab]:
        return AgendaRehab.objects.all()
    
    def filter_by_id(self, id) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id=id).first()
    
    def filter_by_id_paciente(self, id_paciente) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_paciente_area__id_paciente__id=id_paciente).filter(activo=True).order_by("id_dia__id")
    
    def filter_by_id_paciente_exist(self, id_prestacion_paciente) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_prestacion_paciente=AgendaRehab).filter(activo=True).exists()
    
    def filter_by_paciente_area(self, id_paciente_area) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_paciente_area=id_paciente_area).filter(activo=True)
    
    def filter_by_id_profesional_area(self, id_profesional_area) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_profesional_area=id_profesional_area).filter(activo=True)
    
    def filter_by_id_prestacion_paciente(self, id_prestacion_paciente) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_prestacion_paciente=id_prestacion_paciente).filter(activo=True)
    
    def filter_by_id_prestacion_paciente_id_dia(self, id_prestacion_paciente, id_dia) -> Optional[AgendaRehab]:
        try:
            return AgendaRehab.objects.filter(id_prestacion_paciente=id_prestacion_paciente).filter(activo=True).filter(id_dia=id_dia)
        except:
            agenda = None
        return agenda 
    
    def filter_by_activo(self, state) -> List[AgendaRehab]:
        return AgendaRehab.objects.filter(activo=state).order_by("hora_inicio")
    
    def filter_by_activo_profesional(self, state, id_profesional) -> List[AgendaRehab]:
            return AgendaRehab.objects.filter(activo=state).filter(id_profesional_tratamiento__id_profesional__id = id_profesional).order_by("hora_inicio")
    
    def get_by_id(self, id: int) -> Optional[AgendaRehab]:
        try:
            agenda = AgendaRehab.objects.get(id=id)
        except:
            agenda = None
        return agenda 

    def delete(self, agenda: AgendaRehab):
        return agenda.delete()
    
    def delete_by_activo(self, agenda: AgendaRehab):
        agenda.activo=False
        agenda.save()

    def reactivate(self, agenda: AgendaRehab):
        agenda.activo=True
        agenda.save()

    def create(
        self,
        id_usuario: User,
        fecha: str,
        hora_inicio: int,
        hora_fin: int,
        id_dia: Dia,
        tiempo: int,
        id_tratamiento_rehab: Tratamiento,
        id_paciente_area: PacienteArea,
        id_profesional_area: ProfesionalArea,
        observaciones: str,
    ):
        return AgendaRehab.objects.create(
            id_usuario=id_usuario,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            id_dia=id_dia,
            tiempo=tiempo,
            id_tratamiento_rehab=id_tratamiento_rehab,
            id_paciente_area=id_paciente_area,
            id_profesional_area=id_profesional_area,
            observaciones=observaciones,
        )
    
    def update(
        self, 
        agenda: AgendaRehab,
        hora_inicio: int,
        hora_fin: int,
        id_dia: Dia,
        tiempo: int,
        id_tratamiento_rehab: Tratamiento,
        id_profesional_area: ProfesionalArea,
        observaciones: str,
    ) -> AgendaRehab:

        agenda.hora_inicio = hora_inicio
        agenda.hora_fin = hora_fin
        agenda.id_dia = id_dia
        agenda.tiempo=tiempo
        agenda.id_tratamiento_rehab=id_tratamiento_rehab
        agenda.id_profesional_area=id_profesional_area
        agenda.observaciones=observaciones

        agenda.save()

    def end_date(
        self,
        agenda: AgendaRehab,
        fecha_fin: str,
    ) -> AgendaRehab:

        agenda.fecha_fin = fecha_fin

        agenda.save()