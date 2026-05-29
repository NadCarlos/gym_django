from typing import List, Optional

from django.contrib.auth.models import User
from django.utils import timezone

from administracion.models import Paciente, Profesional, Tratamiento
from rehabilitacion.models import Turno


class TurnoRepository:

    def get_all(self) -> List[Turno]:
        return Turno.objects.select_related(
            'paciente_id',
            'paciente_id__id_obra_social',
            'profesional_id',
            'tratamiento_id',
        ).all().order_by('fecha', 'hora')

    def filter_by_profesional_and_fecha(
        self,
        profesional_id=None,
        fecha=None,
    ) -> List[Turno]:
        turnos = self.get_all()

        if profesional_id:
            turnos = turnos.filter(profesional_id_id=profesional_id)

        if fecha:
            turnos = turnos.filter(fecha=fecha)

        return turnos

    def get_by_id(self, id: int) -> Optional[Turno]:
        try:
            turno = Turno.objects.get(id=id)
        except:
            turno = None
        return turno

    def create(
        self,
        paciente: Paciente,
        profesional: Profesional,
        tratamiento: Tratamiento,
        fecha,
        hora,
        estado: str = Turno.ESTADO_PROGRAMADO,
    ) -> Turno:
        return Turno.objects.create(
            paciente_id=paciente,
            profesional_id=profesional,
            tratamiento_id=tratamiento,
            fecha=fecha,
            hora=hora,
            estado=estado,
        )

    def marcar_realizado(self, turno: Turno) -> Turno:
        if turno.estado == Turno.ESTADO_ANULADO:
            return turno

        turno.estado = Turno.ESTADO_REALIZADO
        turno.save()
        return turno

    def anular(self, turno: Turno, motivo_anulacion: str, usuario_anulacion: User) -> Turno:
        if turno.estado == Turno.ESTADO_ANULADO:
            return turno

        turno.estado = Turno.ESTADO_ANULADO
        turno.motivo_anulacion = motivo_anulacion
        turno.usuario_anulacion_id = usuario_anulacion
        turno.fecha_anulacion = timezone.now()
        turno.full_clean()
        turno.save()
        return turno
