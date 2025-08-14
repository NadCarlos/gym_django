from typing import List, Optional

from rehabilitacion.models import Familia


class FamiliaRepository:

    def get_all(self) -> List[Familia]:
        return Familia.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Familia]:
        return Familia.objects.get(id=id)
    
    def filter_by_diagnostico_id(self, id_diagnostico) -> Optional[Familia]:
        return Familia.objects.filter(id_diagnostico=id_diagnostico).first()
