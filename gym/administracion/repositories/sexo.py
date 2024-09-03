from typing import List, Optional

from administracion.models import Sexo


class SexoRepository:

    def get_by_name(self, nombre: str) -> List[Sexo]:
            return Sexo.objects.get(
                nombre=nombre
            )