from typing import List, Optional

from administracion.models import Localidad


class LocalidadRepository:

    def get_by_name(self, nombre: str) -> List[Localidad]:
            return Localidad.objects.get(
                nombre=nombre
            )