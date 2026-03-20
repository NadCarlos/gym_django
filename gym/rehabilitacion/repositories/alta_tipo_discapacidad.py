from typing import List, Optional

from django.contrib.auth.models import User

from rehabilitacion.models import Alta, AltaTipoDiscapacidad, TipoDiscapacidad


class AltaTipoDiscapacidadRepository:

    def get_all(self) -> List[AltaTipoDiscapacidad]:
        return AltaTipoDiscapacidad.objects.all()

    def get_by_id(self, id: int) -> Optional[AltaTipoDiscapacidad]:
        return AltaTipoDiscapacidad.objects.get(id=id)

    def filter_by_id(self, id: int) -> Optional[AltaTipoDiscapacidad]:
        return AltaTipoDiscapacidad.objects.filter(id=id).first()

    def filter_by_alta_id(self, alta_id) -> Optional[AltaTipoDiscapacidad]:
        return AltaTipoDiscapacidad.objects.filter(id_alta=alta_id, activo=True)

    def filter_all_by_alta_id(self, alta_id) -> Optional[AltaTipoDiscapacidad]:
        return AltaTipoDiscapacidad.objects.filter(id_alta=alta_id, activo=True)

    def exists_active_by_alta_and_tipo(
        self,
        alta_id: int,
        tipo_discapacidad_id: int,
        exclude_alta_tipo_discapacidad_id: Optional[int] = None,
    ) -> bool:
        query = AltaTipoDiscapacidad.objects.filter(
            id_alta=alta_id,
            id_tipo_discapacidad=tipo_discapacidad_id,
            activo=True,
        )
        if exclude_alta_tipo_discapacidad_id is not None:
            query = query.exclude(id=exclude_alta_tipo_discapacidad_id)
        return query.exists()

    def has_active_tipo_relation(self, tipo_discapacidad: TipoDiscapacidad) -> bool:
        return AltaTipoDiscapacidad.objects.filter(
            id_tipo_discapacidad=tipo_discapacidad,
            activo=True,
        ).exists()

    def delete_by_activo(self, alta_tipo_discapacidad: AltaTipoDiscapacidad):
        alta_tipo_discapacidad.activo = False
        alta_tipo_discapacidad.save()

    def create(
        self,
        id_alta: Alta,
        id_tipo_discapacidad: TipoDiscapacidad,
        observaciones: str,
        id_usuario: User,
    ):
        return AltaTipoDiscapacidad.objects.create(
            id_alta=id_alta,
            id_tipo_discapacidad=id_tipo_discapacidad,
            observaciones=observaciones,
            id_usuario=id_usuario,
        )

    def update(
        self,
        alta_tipo_discapacidad: AltaTipoDiscapacidad,
        id_tipo_discapacidad: TipoDiscapacidad,
        observaciones: str,
    ):
        alta_tipo_discapacidad.id_tipo_discapacidad = id_tipo_discapacidad
        alta_tipo_discapacidad.observaciones = observaciones
        alta_tipo_discapacidad.save()
        return alta_tipo_discapacidad
