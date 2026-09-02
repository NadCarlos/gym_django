from typing import List, Optional

from django.contrib.auth.models import User
from django.db.models import Q

from administracion.models import Dia, ProfesionalArea
from rehabilitacion.models import DisponibilidadProfesionalRehab


class DisponibilidadProfesionalRehabRepository:

    def filter_by_profesional_area(self, id_profesional_area) -> List[DisponibilidadProfesionalRehab]:
        return DisponibilidadProfesionalRehab.objects.select_related(
            "id_dia",
            "id_profesional_area__id_profesional",
        ).filter(
            id_profesional_area_id=id_profesional_area,
            activo=True,
        ).order_by("id_dia__id", "hora_inicio")

    def get_by_id(self, id: int) -> Optional[DisponibilidadProfesionalRehab]:
        return DisponibilidadProfesionalRehab.objects.filter(id=id).first()

    def has_active_for_profesional_area(self, id_profesional_area) -> bool:
        return DisponibilidadProfesionalRehab.objects.filter(
            id_profesional_area_id=id_profesional_area,
            activo=True,
        ).exists()

    def is_agenda_within_disponibilidad(
        self,
        id_profesional_area,
        id_dia: Dia,
        fecha,
        hora_inicio,
        hora_fin,
    ) -> bool:
        if not self.has_active_for_profesional_area(id_profesional_area):
            return True

        return DisponibilidadProfesionalRehab.objects.filter(
            id_profesional_area_id=id_profesional_area,
            id_dia=id_dia,
            activo=True,
            fecha_inicio__lte=fecha,
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha)
        ).exists()

    def create(
        self,
        id_profesional_area: ProfesionalArea,
        id_dia: Dia,
        hora_inicio,
        hora_fin,
        fecha_inicio,
        fecha_fin,
        id_usuario: User,
    ) -> DisponibilidadProfesionalRehab:
        return DisponibilidadProfesionalRehab.objects.create(
            id_profesional_area=id_profesional_area,
            id_dia=id_dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_usuario=id_usuario,
        )

    def update(
        self,
        disponibilidad: DisponibilidadProfesionalRehab,
        id_dia: Dia,
        hora_inicio,
        hora_fin,
        fecha_inicio,
        fecha_fin,
    ) -> DisponibilidadProfesionalRehab:
        disponibilidad.id_dia = id_dia
        disponibilidad.hora_inicio = hora_inicio
        disponibilidad.hora_fin = hora_fin
        disponibilidad.fecha_inicio = fecha_inicio
        disponibilidad.fecha_fin = fecha_fin
        disponibilidad.save(
            update_fields=[
                "id_dia",
                "hora_inicio",
                "hora_fin",
                "fecha_inicio",
                "fecha_fin",
            ]
        )
        return disponibilidad

    def deactivate(self, disponibilidad: DisponibilidadProfesionalRehab) -> None:
        disponibilidad.activo = False
        disponibilidad.save(update_fields=["activo"])
