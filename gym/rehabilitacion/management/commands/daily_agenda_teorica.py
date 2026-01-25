from rehabilitacion.repositories.asistencia_teorica import AsistenciaRehabRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository


asistenciaTeoricaRepo = AsistenciaRehabRepository()
agendaRehabRepo = AgendaRehabRepository()


def daily_agenda_teorica_func():
    agendas = agendaRehabRepo.filter_by_dia(id_dia=1)
    for agenda in agendas:
        asistenciaTeoricaRepo.create(
            id_agenda_rehab=agenda
        )