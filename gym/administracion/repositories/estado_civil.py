from typing import List, Optional

from administracion.models import EstadoCivil


class EstadoCivilRepository:

    def get_by_name(self, nombre: str) -> List[EstadoCivil]:
            return EstadoCivil.objects.get(
                nombre=nombre
            )