from typing import List, Optional

from rehabilitacion.models import Alta, PacienteRehabilitacion, Diagnostico


class AltaRepository:

    def get_all(self) -> List[Alta]:
        return Alta.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Alta]:
        return Alta.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Alta]:
        return Alta.objects.filter(id=id)
    
    def create(
        self,
        fecha: str,
        id_diagnostico: Diagnostico,
        id_paciente_rehabilitacion: PacienteRehabilitacion,
        ):
        return Alta.objects.create(
            fecha=fecha,
            id_diagnostico=id_diagnostico,
            id_paciente_rehabilitacion=id_paciente_rehabilitacion,
        )