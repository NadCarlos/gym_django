from typing import List, Optional

from rehabilitacion.models import TipoDiscapacidad


class TipoDiscapacidadRepository:

    def get_all(self) -> List[TipoDiscapacidad]:
        return TipoDiscapacidad.objects.all()
    
    def get_by_id(self, id: int) -> Optional[TipoDiscapacidad]:
        return TipoDiscapacidad.objects.get(id=id)
    
    def filter_by_diagnostico_etiologico_id(self, id_diagnostico_etiologico) -> Optional[TipoDiscapacidad]:
        return TipoDiscapacidad.objects.filter(id_diagnostico_etiologico=id_diagnostico_etiologico).first()

    def create(
        self,
        nombre: str,
    ):
        return TipoDiscapacidad.objects.create(
            nombre=nombre,
        )