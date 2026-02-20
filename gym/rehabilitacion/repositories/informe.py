from typing import List, Optional

from rehabilitacion.models import Informe 


class InformeRepository:

    def get_all(self) -> List[Informe]:
        return Informe.objects.all()

    def get_by_id(self, id: int) -> Optional[Informe]:
        return Informe.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Informe]:
        return Informe.objects.filter(id=id)
    
    def filter_by_paciente_id(self, paciente_id) -> Optional[Informe]:
        return Informe.objects.filter(id_paciente=paciente_id)
    
    def create(
        self,
        nombre: str,
        id: Informe,
        ):
        return Informe.objects.create(
            nombre=nombre,
        )