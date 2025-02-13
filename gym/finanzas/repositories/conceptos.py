from typing import List, Optional

from finanzas.models import Concepto


class ConceptoRepository:

    def get_all(self) -> List[Concepto]:
        return Concepto.objects.all()
    
    def filter_by_id(self, id) -> Optional[Concepto]:
        return Concepto.objects.filter(id=id).first()
    
    def create(
        self,
        nombre: str,
    ):
        return Concepto.objects.create(
            nombre=nombre,
        )