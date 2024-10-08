from typing import List, Optional

from administracion.models import Tratamiento


class PacienteRepository:

    def get_all(self) -> List[Tratamiento]:
        return Tratamiento.objects.all()
    
    def filter_by_id(self) -> Optional[Tratamiento]:
        return Tratamiento.objects.filter(id=id).first()
    
    def filter_by_activo(self) -> List[Tratamiento]:
        return Tratamiento.objects.filter(
            activo=True
        )

    def get_by_id(self, id: int) -> Optional[Tratamiento]:
        try:
            tratamiento = Tratamiento.objects.get(id=id)
        except:
            tratamiento = None
        return tratamiento 
    
    def delete(self, tratamiento: Tratamiento):
        return tratamiento.delete()
    
    def delete_by_activo(self, tratamiento: Tratamiento):
        tratamiento.activo=False
        tratamiento.save()

    def create(
        self,
        nombre: str,
    ):
        return Tratamiento.objects.create(
            nombre=nombre,
        )
    
    def update(
        self, 
        tratamiento: Tratamiento,
        nombre: str,
    ) -> Tratamiento:
        tratamiento.nombre = nombre
        tratamiento.save()