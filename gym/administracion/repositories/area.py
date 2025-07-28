from typing import List, Optional

from administracion.models import Area


class AreaRepository:

    def get_all(self) -> List[Area]:
        return Area.objects.all()
    
    def get_by_id(self, id: int) -> Optional[Area]:
        return Area.objects.get(id=id)