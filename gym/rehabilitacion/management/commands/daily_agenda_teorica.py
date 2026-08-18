from datetime import date
import logging

from django.core.management.base import BaseCommand
from rehabilitacion.repositories.asistencia_teorica import AsistenciaRehabRepository
from rehabilitacion.repositories.agenda_rehab import AgendaRehabRepository


logger = logging.getLogger("cermed.cron")
asistenciaTeoricaRepo = AsistenciaRehabRepository()
agendaRehabRepo = AgendaRehabRepository()
REHABILITACION_AREA_ID = 2


def daily_agenda_teorica_func(fecha=None):
    today = fecha or date.today()
    if today.weekday() > 4:
        resumen = {
            "fecha": today,
            "encontradas": 0,
            "creadas": 0,
            "existentes": 0,
            "errores": 0,
        }
        logger.info(
            "Agenda teorica rehab | Fecha: %(fecha)s | Agendas encontradas: %(encontradas)s | "
            "Creadas: %(creadas)s | Existentes: %(existentes)s | Errores: %(errores)s",
            resumen,
        )
        return resumen

    dia = today.weekday() + 1
    agendas = agendaRehabRepo.filter_by_dia(
        id_dia=dia,
        id_area=REHABILITACION_AREA_ID,
    )
    resumen = {
        "fecha": today,
        "encontradas": agendas.count(),
        "creadas": 0,
        "existentes": 0,
        "errores": 0,
    }

    for agenda in agendas:
        if asistenciaTeoricaRepo.filter_by_agenda_date(
            id_agenda_rehab=agenda.id,
            fecha=today,
        ).exists():
            resumen["existentes"] += 1
            continue

        try:
            asistenciaTeoricaRepo.create(
                id_agenda_rehab=agenda,
                fecha=today,
            )
            resumen["creadas"] += 1
        except Exception:
            resumen["errores"] += 1
            logger.exception(
                "No se pudo crear la asistencia teorica para la agenda rehab %s",
                agenda.id,
            )

    logger.info(
        "Agenda teorica rehab | Fecha: %(fecha)s | Agendas encontradas: %(encontradas)s | "
        "Creadas: %(creadas)s | Existentes: %(existentes)s | Errores: %(errores)s",
        resumen,
    )
    return resumen


class Command(BaseCommand):
    help = "Genera las asistencias teoricas de rehabilitacion para una fecha."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fecha",
            type=lambda value: date.fromisoformat(value),
            help="Fecha a procesar en formato YYYY-MM-DD. Por defecto usa la fecha actual.",
        )

    def handle(self, *args, **options):
        resumen = daily_agenda_teorica_func(fecha=options.get("fecha"))
        self.stdout.write(
            self.style.SUCCESS(
                "Fecha: {fecha} | Agendas encontradas: {encontradas} | "
                "Creadas: {creadas} | Existentes: {existentes} | Errores: {errores}".format(
                    **resumen
                )
            )
        )
