from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Dia, PrestacionPaciente, ProfesionalTratamiento
from rehabilitacion.models import AgendaRehab


class AgendaRehabRepository:

    def get_all(self) -> List[AgendaRehab]:
        return AgendaRehab.objects.all()
    
    def filter_by_id(self) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id=id).first()
    
    def filter_by_id_paciente(self, id_prestacion_paciente) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_prestacion_paciente=id_prestacion_paciente).filter(activo=True)
    
    def filter_by_id_paciente_exist(self, id_prestacion_paciente) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_prestacion_paciente=AgendaRehab).filter(activo=True).exists()
    
    def filter_by_id_profesional(self, id_profesional_tratamiento) -> Optional[AgendaRehab]:
        return AgendaRehab.objects.filter(id_profesional_tratamiento=id_profesional_tratamiento).filter(activo=True)
    
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
        id_prestacion_paciente: PrestacionPaciente,
        id_profesional_tratamiento: ProfesionalTratamiento,
        id_dia: Dia,
        tiempo: int,
    ):
        return AgendaRehab.objects.create(
            id_usuario=id_usuario,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            id_prestacion_paciente=id_prestacion_paciente,
            id_profesional_tratamiento=id_profesional_tratamiento,
            id_dia=id_dia,
            tiempo=tiempo,
        )
    
    def update(
        self, 
        agenda: AgendaRehab,
        hora_inicio: int,
        hora_fin: int,
        id_profesional_tratamiento: ProfesionalTratamiento,
        id_dia: Dia,
        tiempo: int,
    ) -> AgendaRehab:

        agenda.hora_inicio = hora_inicio
        agenda.hora_fin = hora_fin
        agenda.id_profesional_tratamiento=id_profesional_tratamiento
        agenda.id_dia = id_dia
        tiempo=tiempo,

        agenda.save()

    def end_date(
        self,
        agenda: AgendaRehab,
        fecha_fin: str,
    ) -> AgendaRehab:

        agenda.fecha_fin = fecha_fin

        agenda.save()