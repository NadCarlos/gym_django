from typing import List, Optional

from rehabilitacion.models import Diagnostico, Familia


class DiagnosticoRepository:

    def get_all(self) -> List[Diagnostico]:
        return Diagnostico.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Diagnostico]:
        return Diagnostico.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Diagnostico]:
        return Diagnostico.objects.filter(id=id)
    
    def filter_by_familia_id(self, id_familia) -> Optional[Diagnostico]:
        return Diagnostico.objects.filter(id_familia=id_familia).first()
    
    def create(
        self,
        nombre: str,
        id_familia: Familia,
        ):
        return Diagnostico.objects.create(
            nombre=nombre,
            id_familia=id_familia,
        )