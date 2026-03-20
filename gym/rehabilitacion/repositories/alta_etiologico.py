from typing import List, Optional

from django.contrib.auth.models import User

from rehabilitacion.models import Alta, AltaEtiologico, DiagnosticoEtiologico


class AltaEtiologicoRepository:

    def get_all(self) -> List[AltaEtiologico]:
        return AltaEtiologico.objects.all()

    def get_by_id(self, id: int) -> Optional[AltaEtiologico]:
        return AltaEtiologico.objects.get(id=id)

    def filter_by_id(self, id: int) -> Optional[AltaEtiologico]:
        return AltaEtiologico.objects.filter(id=id).first()

    def filter_by_alta_id(self, alta_id) -> Optional[AltaEtiologico]:
        return AltaEtiologico.objects.filter(id_alta=alta_id, activo=True)

    def filter_all_by_alta_id(self, alta_id) -> Optional[AltaEtiologico]:
        return AltaEtiologico.objects.filter(id_alta=alta_id, activo=True)

    def exists_active_by_alta_and_diagnostico(
        self,
        alta_id: int,
        diagnostico_etiologico_id: int,
        exclude_alta_etiologico_id: Optional[int] = None,
    ) -> bool:
        query = AltaEtiologico.objects.filter(
            id_alta=alta_id,
            id_diagnostico_etiologico=diagnostico_etiologico_id,
            activo=True,
        )
        if exclude_alta_etiologico_id is not None:
            query = query.exclude(id=exclude_alta_etiologico_id)
        return query.exists()

    def has_active_diagnostico_relation(self, diagnostico_etiologico: DiagnosticoEtiologico) -> bool:
        return AltaEtiologico.objects.filter(
            id_diagnostico_etiologico=diagnostico_etiologico,
            activo=True,
        ).exists()

    def delete_by_activo(self, alta_etiologico: AltaEtiologico):
        alta_etiologico.activo = False
        alta_etiologico.save()

    def create(
        self,
        id_alta: Alta,
        id_diagnostico_etiologico: DiagnosticoEtiologico,
        observaciones: str,
        id_usuario: User,
    ):
        return AltaEtiologico.objects.create(
            id_alta=id_alta,
            id_diagnostico_etiologico=id_diagnostico_etiologico,
            observaciones=observaciones,
            id_usuario=id_usuario,
        )

    def update(
        self,
        alta_etiologico: AltaEtiologico,
        id_diagnostico_etiologico: DiagnosticoEtiologico,
        observaciones: str,
    ):
        alta_etiologico.id_diagnostico_etiologico = id_diagnostico_etiologico
        alta_etiologico.observaciones = observaciones
        alta_etiologico.save()
        return alta_etiologico
