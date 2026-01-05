from typing import List, Optional

from administracion.models import EstadoCivil


class EstadoCivilRepository:

    def get_by_name(self, nombre: str) -> List[EstadoCivil]:
            return EstadoCivil.objects.get(
                nombre=nombre
            )
    
    def get_by_id(self, id: int) -> Optional[EstadoCivil]:
        try:
            estado_civil = EstadoCivil.objects.get(id=id)
        except:
            estado_civil = None
        return estado_civil