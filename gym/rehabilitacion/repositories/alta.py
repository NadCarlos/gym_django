from typing import List, Optional

from django.db.models import Prefetch

from rehabilitacion.models import (
    Alta,
    AltaEtiologico,
    AltaFuncional,
    AltaTipoDiscapacidad,
    PacienteRehabilitacion,
)


class AltaRepository:

    def get_all(self) -> List[Alta]:
        return Alta.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Alta]:
        return Alta.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Alta]:
        return Alta.objects.filter(id=id).first()
    
    def filter_by_id_activa(self, id_paciente_rehab) -> Optional[Alta]:
        return Alta.objects.filter(
            id_paciente_rehabilitacion=id_paciente_rehab,
            dado_alta=0,
        ).first()
    
    def filter_by_paciente_rehab_id(self, id_paciente_rehab) -> Optional[Alta]:
        return Alta.objects.filter(id_paciente_rehabilitacion=id_paciente_rehab).order_by("dado_alta", "-fecha", "-id")

    def filter_for_patient_detail(self, id_paciente_rehab):
        return Alta.objects.filter(
            id_paciente_rehabilitacion=id_paciente_rehab,
        ).order_by(
            "dado_alta", "-fecha", "-id",
        ).prefetch_related(
            Prefetch(
                "id_alta_tipo_discapacidad",
                queryset=AltaTipoDiscapacidad.objects.filter(activo=True).select_related(
                    "id_tipo_discapacidad",
                ),
                to_attr="altas_tipo_discapacidad",
            ),
            Prefetch(
                "id_alta_etiologico",
                queryset=AltaEtiologico.objects.filter(activo=True).select_related(
                    "id_diagnostico_etiologico",
                ),
                to_attr="altas_etiologicos",
            ),
            Prefetch(
                "id_diagnostico_funcional",
                queryset=AltaFuncional.objects.filter(activo=True).select_related(
                    "id_diagnostico_funcional",
                ),
                to_attr="altas_funcionales",
            ),
        )

    def filter_by_paciente_rehab_id_activa(self, id_paciente_rehab) -> Optional[Alta]:
            return Alta.objects.filter(id_paciente_rehabilitacion=id_paciente_rehab).filter(dado_alta=False).first()
    
    def tiene_alta_activa(self, id_paciente_rehab) -> Optional[Alta]:
        return Alta.objects.filter(id_paciente_rehabilitacion=id_paciente_rehab).filter(dado_alta=False).exists()
    
    def create(
        self,
        fecha: str,
        id_paciente_rehabilitacion: PacienteRehabilitacion,
        ):
        return Alta.objects.create(
            fecha=fecha,
            id_paciente_rehabilitacion=id_paciente_rehabilitacion,
        )
    
    def terminate(
            self,
            alta: Alta,
            fecha_alta: str,
            dado_alta: bool,
        )->Alta:
        alta.fecha_alta=fecha_alta
        alta.dado_alta=dado_alta

        alta.save()
        return alta
