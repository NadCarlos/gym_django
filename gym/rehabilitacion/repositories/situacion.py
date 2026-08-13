from typing import List, Optional

from django.utils import timezone

from rehabilitacion.models import (
    PacienteRehabilitacion,
    PacienteRehabilitacionSituacion,
    Situacion,
)


class SituacionRepository:
    CARGA_INICIAL_ID = 1
    CARGA_INICIAL_NOMBRE = "Carga inicial"

    def get_carga_inicial(self) -> Situacion:
        situacion, _ = Situacion.objects.get_or_create(
            idsituacion=self.CARGA_INICIAL_ID,
            defaults={"nombre": self.CARGA_INICIAL_NOMBRE},
        )
        return situacion

    def get_all(self) -> List[Situacion]:
        return Situacion.objects.all().order_by("nombre")

    def get_by_id(self, idsituacion: int) -> Optional[Situacion]:
        return Situacion.objects.filter(idsituacion=idsituacion).first()


class PacienteRehabilitacionSituacionRepository:
    
    def get_ultima(
        self,
        id_paciente_rehabilitacion: int,
    ) -> Optional[PacienteRehabilitacionSituacion]:
        return (
            PacienteRehabilitacionSituacion.objects
            .filter(idpacienterehabilitacion_id=id_paciente_rehabilitacion)
            .select_related("idsituacion")
            .order_by("-fecha", "-id")
            .first()
        )

    def get_historial(
        self,
        id_paciente_rehabilitacion: int,
    ) -> List[PacienteRehabilitacionSituacion]:
        return (
            PacienteRehabilitacionSituacion.objects
            .filter(idpacienterehabilitacion_id=id_paciente_rehabilitacion)
            .select_related("idsituacion")
            .order_by("-fecha", "-id")
        )

    def create(
        self,
        idpacienterehabilitacion: PacienteRehabilitacion,
        idsituacion: Situacion,
        fecha,
        observaciones: str = None,
    ) -> PacienteRehabilitacionSituacion:
        return PacienteRehabilitacionSituacion.objects.create(
            idpacienterehabilitacion=idpacienterehabilitacion,
            idsituacion=idsituacion,
            fecha=fecha,
            observaciones=observaciones,
        )

    def create_carga_inicial(
        self,
        idpacienterehabilitacion: PacienteRehabilitacion,
    ) -> PacienteRehabilitacionSituacion:
        situacion = SituacionRepository().get_carga_inicial()
        return self.create(
            idpacienterehabilitacion=idpacienterehabilitacion,
            idsituacion=situacion,
            fecha=timezone.now(),
        )
