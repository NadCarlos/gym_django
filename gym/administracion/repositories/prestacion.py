from typing import List, Optional

from administracion.models import Prestacion


class PrestacionRepository:

    def get_all(self) -> List[Prestacion]:
        return Prestacion.objects.all()
    
    def filter_by_id(self) -> Optional[Prestacion]:
        return Prestacion.objects.filter(id=id).first()
    
    def get_by_id(self, id: int) -> Optional[Prestacion]:
        try:
            prestacion = Prestacion.objects.get(id=id)
        except:
            prestacion = None
        return prestacion
    
    def delete(self, prestacion: Prestacion):
        return prestacion.delete()
    
    def delete_by_activo(self, prestacion: Prestacion):
        prestacion.activo=False
        prestacion.save()
    
    def create(
        self,
        nombre: str,
        descripcion: str,
    ):
        return Prestacion.objects.create(
            nombre=nombre,
            descripcion=descripcion,
        )
    
    def update(
        self, 
        prestacion: Prestacion,
        nombre: str,
        descripcion: str,
    ) -> Prestacion:

        prestacion.nombre = nombre
        prestacion.descripcion = descripcion

        prestacion.save()