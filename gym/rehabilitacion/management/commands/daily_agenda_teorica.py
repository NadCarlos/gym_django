from datetime import date

from rehabilitacion.repositories.asistencia_teorica import AsistenciaRehabRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository


asistenciaTeoricaRepo = AsistenciaRehabRepository()
agendaRehabRepo = AgendaRehabRepository()


def daily_agenda_teorica_func():
    try:
        dias = [1,2,3,4,5]
        today = date.today()
        dia = dias[today.weekday()]
        agendas = agendaRehabRepo.filter_by_dia(id_dia=dia)
        for agenda in agendas:
            asistenciaTeoricaRepo.create(
                id_agenda_rehab=agenda
            )
    except:
        pass