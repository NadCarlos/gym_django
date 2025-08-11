from typing import List, Optional

from rehabilitacion.models import Derivador


class DerivadorRepository:

    def filter_by_id(self, id) -> Optional[Derivador]:
        return Derivador.objects.filter(id=id).first()