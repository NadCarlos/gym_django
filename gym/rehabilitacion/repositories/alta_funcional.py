from typing import List, Optional

from django.contrib.auth.models import User
from rehabilitacion.models import AltaFuncional, Alta, DiagnosticoFuncional


class AltaFuncionalRepository:

    def get_all(self) -> List[AltaFuncional]:
        return AltaFuncional.objects.all()
    
    def get_by_id(self, id: int) -> Optional[AltaFuncional]:
        return AltaFuncional.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[AltaFuncional]:
        return AltaFuncional.objects.filter(id=id).first()
    
    def create(
        self,
        id_alta: Alta,
        id_diagnostico_funcional: DiagnosticoFuncional,
        observaciones: str,
        id_usuario: User,
        ):
        return AltaFuncional.objects.create(
            id_alta=id_alta,
            id_diagnostico_funcional=id_diagnostico_funcional,
            observaciones=observaciones,
            id_usuario=id_usuario,
        )