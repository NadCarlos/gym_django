from typing import List, Optional

from rehabilitacion.models import EstadoCertificado


class EstadoCertificadoRepository:

    def filter_by_id(self, id) -> Optional[EstadoCertificado]:
        return EstadoCertificado.objects.filter(id=id).first()