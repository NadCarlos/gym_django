from typing import List, Optional

from django.contrib.auth.models import User
from administracion.models import Agenda, Dia, PrestacionPaciente, ProfesionalTratamiento


class AgendaRepository:

    def get_all(self) -> List[Agenda]:
        return Agenda.objects.all()
    
    def filter_by_id(self) -> Optional[Agenda]:
        return Agenda.objects.filter(id=id).first()
    
    def filter_by_activo(self, state) -> List[Agenda]:
        return Agenda.objects.filter(activo=state)

    def get_by_id(self, id: int) -> Optional[Agenda]:
        try:
            agenda = Agenda.objects.get(id=id)
        except:
            agenda = None
        return agenda 

    def delete(self, agenda: Agenda):
        return agenda.delete()
    
    def delete_by_activo(self, agenda: Agenda):
        agenda.activo=False
        agenda.save()

    def reactivate(self, agenda: Agenda):
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
        return Agenda.objects.create(
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
        agenda: Agenda,
        id_usuario: User,
        fecha: str,
        hora_inicio: int,
        hora_fin: int,
        id_prestacion_paciente: PrestacionPaciente,
        id_profesional_tratamiento: ProfesionalTratamiento,
        id_dia: Dia,
        tiempo: int,
    ) -> Agenda:

        agenda.id_usuario = id_usuario
        agenda.id_usuario = id_usuario
        agenda.fecha = fecha
        agenda.hora_inicio = hora_inicio
        agenda.hora_fin = hora_fin
        agenda.id_prestacion_paciente = id_prestacion_paciente
        agenda.id_profesional_tratamiento=id_profesional_tratamiento
        agenda.id_dia = id_dia
        agenda.tiempo = tiempo

        agenda.save()